#include<cstddef>
#include<iostream>
#include<string>
#include<fstream>
#include<sstream>
#include<vector>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <isa-l.h>	
#include <cstring>

#define MMAX 255
#define KMAX 255

typedef unsigned char u8;

using namespace std;

static int gf_gen_decode_matrix_simple(u8 * encode_matrix,
				       u8 * decode_matrix,
				       u8 * invert_matrix,
				       u8 * temp_matrix,
				       u8 * decode_index,
				       u8 * frag_err_list, int nerrs, int k, int m);

string convertToString(u8* a,int size)
{
    int i;
    // int size = sizeof(a)/sizeof(a[0]);
    // cout<<size<<endl;
    string s = "";

    for (i = 0; i < size; i++) {
        s = s + (char) a[i];
    }
    return s;
}

int file_size(int code_length){
    string str;
    for(int i=0;i<code_length;i++){
        string filename = "parts/myfile_"+to_string(i+1);
        // filename += ".bin"; 
        ifstream f(filename, ifstream::binary); //taking file as inputstream
        // cout<<filename<<endl;
        if(f) {
            ostringstream ss;
            ss << f.rdbuf(); // reading data
            str = ss.str();
            break;
        }
        f.close();
    }
    return str.size();
}

string xor_strings(string s1,string s2){
    string result = "";
    result.resize(s1.size(),0x00);
    for(int i=0;i<s1.size();i++)
        result[i] = s1[i] ^ s2[i];

    return result;
}

string get_data_from_local(vector<string> local_group,string local_group_parity){
    // vector<string> local_group is the list of strings with the exception of 1 data block
    string result = xor_strings(local_group[0],local_group[1]);

    for(int i=2;i<local_group.size();i++){
        result = xor_strings(local_group[i] , result);
    }

    result = xor_strings(local_group_parity,result);

    return result;
}

int main(int argc, char *argv[]){

	int k = 7, r = 2;
    int n = k+r;
    int l = 3; // Number of local groups

	int nerrs = 0;

	// Fragment buffer pointers
	u8 *frag_ptrs[MMAX];
	u8 *frag_ptrs_recover[MMAX];
	u8 *recover_srcs[KMAX];
	u8 *recover_outp[KMAX];
	u8 frag_err_list[MMAX];

	// Coefficient matrices
	u8 *encode_matrix, *decode_matrix;
	u8 *invert_matrix, *temp_matrix;
	u8 *g_tbls;
	u8 decode_index[MMAX];


    int i;
    string main_extension = "";
    string main_filename = "hexdump";
    cout<<"MAIN FILENAME "<<main_filename<<endl;

	printf("ec_simple_example:\n");
    int parts = file_size(n);
    cout<<"PARTS : "<<parts<<endl;
	// Allocate coding matrices
	encode_matrix = (u8*) malloc(n * k);
	decode_matrix = (u8*) malloc(n * k);
	invert_matrix = (u8*) malloc(n * k);
	temp_matrix = (u8*) malloc(n * k);
	g_tbls = (u8*) malloc(k * r * 32);

    if (encode_matrix == NULL || decode_matrix == NULL
	    || invert_matrix == NULL || temp_matrix == NULL || g_tbls == NULL) {
		printf("Test failure! Error with malloc\n");
		return -1;
	}
	// Allocate the src & parity buffers
	for (i = 0; i < n; i++) {
		if (NULL == (frag_ptrs[i] = (u8*) malloc(parts))) {
			printf("alloc error: Fail\n");
			return -1;
		}
	}

	// Allocate buffers for recovered data
	for (i = 0; i < r; i++) {
		if (NULL == (recover_outp[i] = (u8*) malloc(parts))) {
			printf("alloc error: Fail\n");
			return -1;
		}
	}



    cout<<"READ FILES"<<endl;
    for(int i=0;i<n;i++){
        // if(i <= 12) continue;

        string filename = "parts/myfile_"+to_string(i+1);
        ifstream f(filename, ifstream::binary); //taking file as inputstream
        string str;
        // cout<<filename<<endl;
        if(f) {
            ostringstream ss;
            ss << f.rdbuf(); // reading data
            str = ss.str();
    
            f.close();
            for(int j=0;j<parts;j++){
                frag_ptrs[i][j] = str[j];
            }
        } else{
            frag_err_list[nerrs++] = i;
            for(int j=0;j<parts;j++){
                frag_ptrs[i][j] = 0;
            }
        }
    }
    int j;
    for (i = 0; i < n; i++){
		for (j = 0; j < 20; j++){
            cout<<(int) frag_ptrs[i][j]<<" ";
        }
        cout<<endl;
       // cout<<convertToString(frag_ptrs[i],parts)<<endl;
    }
    cout<<endl;
	if (nerrs <= 0)
		return 0;
    if(nerrs > r) {
        cout<<"NOT DECODABLE"<<endl;
        return -1;
    }
    for(i=0;i<nerrs;i++)
        printf("Error at postition - %d\n",frag_err_list[i]);
   
    // Pick an encode matrix. A Cauchy matrix is a good choice as even
    // large k are always invertable keeping the recovery rule simple.
	gf_gen_cauchy1_matrix(encode_matrix, n, k);

	// Initialize g_tbls from encode matrix
	ec_init_tables(k, r, &encode_matrix[k * k], g_tbls);


	// Find a decode matrix to regenerate all erasures from remaining frags
	int ret = gf_gen_decode_matrix_simple(encode_matrix, decode_matrix,
					  invert_matrix, temp_matrix, decode_index,
					  frag_err_list, nerrs, k, n);
	if (ret != 0) {
		printf("Fail on generate decode matrix\n");
		return -1;
	}
	// Pack recovery array pointers as list of valid fragments
	for (i = 0; i < k; i++)
		recover_srcs[i] = frag_ptrs[decode_index[i]];

	// Recover data
	ec_init_tables(k, nerrs, decode_matrix, g_tbls);
	ec_encode_data(parts, k, nerrs, g_tbls, recover_srcs, recover_outp);
	
    for (i = 0; i < nerrs; i++) {
        for(int j=0;j<parts;j++){
            frag_ptrs[frag_err_list[i]][j]=recover_outp[i][j];
        }
    }

    for (i = 0; i < n; i++){
		for (j = 0; j < 20; j++){
            cout<<(int) frag_ptrs[i][j]<<" ";
        }
        cout<<endl;
       // cout<<convertToString(frag_ptrs[i],parts)<<endl;
    }

    cout<<endl;

    string reconstructed_message = "";
    for(i=0;i<k;i++)
        reconstructed_message += convertToString(frag_ptrs[i],parts);

    // cout<<reconstructed_message.size()<<endl;
    // for(int j=0;j<parts;j++)
    //     cout<<(k-1)*parts+j<<" "<<reconstructed_message[(k-1)*parts+j]<<endl;
    // cout<<endl;
    // cout<<reconstructed_message<<endl;
    // cout<<reconstructed_message.find('\0')<<endl;
    reconstructed_message.erase(reconstructed_message.find('\0'), reconstructed_message.size()-reconstructed_message.find('\0'));

    // cout<<reconstructed_message.size()<<endl;
    cout<<"WRITE RECONSTRUCT FILE"<<endl;
    string filename = main_filename+"_reconstruct"+main_extension;
    ofstream outfile(filename, ios::out | ios::binary);
    const char *array = reconstructed_message.c_str();
    outfile.write(array,reconstructed_message.size());
    outfile.close();

    exit(0);
}


static int gf_gen_decode_matrix_simple(u8 * encode_matrix,
				       u8 * decode_matrix,
				       u8 * invert_matrix,
				       u8 * temp_matrix,
				       u8 * decode_index, u8 * frag_err_list, int nerrs, int k,
				       int m)
{
	int i, j, p, r;
	int nsrcerrs = 0;
	u8 s, *b = temp_matrix;
	u8 frag_in_err[MMAX];

	memset(frag_in_err, 0, sizeof(frag_in_err));

	// Order the fragments in erasure for easier sorting
	for (i = 0; i < nerrs; i++) {
		if (frag_err_list[i] < k)
			nsrcerrs++;
		frag_in_err[frag_err_list[i]] = 1;
	}

	// Construct b (matrix that encoded remaining frags) by removing erased rows
	for (i = 0, r = 0; i < k; i++, r++) {
		while (frag_in_err[r])
			r++;
		for (j = 0; j < k; j++)
			b[k * i + j] = encode_matrix[k * r + j];
		decode_index[i] = r;
	}

	// Invert matrix to get recovery matrix
	if (gf_invert_matrix(b, invert_matrix, k) < 0)
		return -1;

	// Get decode matrix with only wanted recovery rows
	for (i = 0; i < nerrs; i++) {
		if (frag_err_list[i] < k)	// A src err
			for (j = 0; j < k; j++)
				decode_matrix[k * i + j] =
				    invert_matrix[k * frag_err_list[i] + j];
	}

	// For non-src (parity) erasures need to multiply encode matrix * invert
	for (p = 0; p < nerrs; p++) {
		if (frag_err_list[p] >= k) {	// A parity err
			for (i = 0; i < k; i++) {
				s = 0;
				for (j = 0; j < k; j++)
					s ^= gf_mul(invert_matrix[j * k + i],
						    encode_matrix[k * frag_err_list[p] + j]);
				decode_matrix[k * p + i] = s;
			}
		}
	}
	return 0;
}
