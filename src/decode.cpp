#include<algorithm>
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
#include <chrono>

#define MMAX 255
#define KMAX 255

typedef unsigned char u8;

using namespace std;
using namespace std::chrono;

static int gf_gen_decode_matrix_simple(u8 * encode_matrix,
				       u8 * decode_matrix,
				       u8 * invert_matrix,
				       u8 * temp_matrix,
				       u8 * decode_index, vector<int> frag_err_list, int nerrs, int k,
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

void decode_data(int n,int k, int r, int parts,vector<int> frag_err_list,u8 **frag_ptrs,u8 **recover_srcs,u8 **recover_outp){

		// Coefficient matrices
	u8 *encode_matrix, *decode_matrix;
	u8 *invert_matrix, *temp_matrix;
	u8 *g_tbls;
	u8 decode_index[MMAX];

	// Allocate coding matrices
	encode_matrix = (u8*) malloc(n * k);
	decode_matrix = (u8*) malloc(n * k);
	invert_matrix = (u8*) malloc(n * k);
	temp_matrix = (u8*) malloc(n * k);
	g_tbls = (u8*) malloc(k * r * 32);

	if (encode_matrix == NULL || decode_matrix == NULL
	    || invert_matrix == NULL || temp_matrix == NULL || g_tbls == NULL) {
		printf("Test failure! Error with malloc\n");
		return ;
	}
	int nerrs = frag_err_list.size();
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
		return;
	}

	int i, j;
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
}

void xor_func(u8* res, u8* s,int size){
	for(int i=0;i<size;i++){
		res[i] = (u8)((int)res[i] ^ (int)s[i]);
	}
}


vector<int> decode_local_groups(int n, int k, int r, int l, int parts, vector<int> frag_present_list,vector<int> frag_err_list,u8 **frag_ptrs){
	
	int i,j;
	
	for(i = 0;i<l;i++){
		int count = 0;
		int curr = 0;
		vector<int> local_group;

        string filename = "parts/myfile_local_"+to_string(i+1);
        ifstream f(filename, ifstream::binary); //taking file as inputstream
        string str;

		if(!f) continue;


		while((curr != frag_present_list.size())){
			if(frag_present_list[curr]>=((i)*(k/l)) && frag_present_list[curr]<((i+1)*(k/l))){
				local_group.push_back(frag_present_list[curr]);
				// cout<<frag_present_list[curr]<<endl;
				count++;
			}
			// cout<<"HERE"<<endl;
			curr++;
		}
		// cout<<"count - "<<count<<endl;
		if(count == ((k/l)-1)){

			cout<<"DECODING LOCAL GROUP "<<(i+1)<<endl;
			
			ostringstream ss;
            ss << f.rdbuf(); // reading data
            str = ss.str();
            f.close();

			int missing_idx;
			
			for(int j=((i)*(k/l));j<((i+1)*(k/l));j++){
				auto it = find(local_group.begin(), local_group.end(), j);
				if (it == local_group.end()){
					missing_idx = j;
					break;
				}
			}

			cout<<"MISSING INDEX "<<missing_idx<<endl;
			for(int j=0;j<parts;j++){
                frag_ptrs[missing_idx][j] = (u8) str[j];
            }
			// for(int k=0;k<20;k++){
			// 	cout<<(int) frag_ptrs[missing_idx][k]<<" ";
			// }
			// cout<<endl;

			for(auto it:local_group){
				// cout<<"PRESENT INDEX "<<it<<endl;
				xor_func(frag_ptrs[missing_idx],frag_ptrs[it],parts);
				// 		for(int k=0;k<20;k++){
				// cout<<(int) frag_ptrs[missing_idx][k]<<" ";
			// }
			// cout<<endl;

			}
			// cout<<endl;

			frag_err_list.erase(std::find(frag_err_list.begin(),frag_err_list.end(),missing_idx));
			// remove(frag_err_list.begin(),frag_err_list.end(),missing_idx);

		}
	}
	return frag_err_list;
}

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
        ifstream f(filename, ifstream::binary); 
        if(f) {
            ostringstream ss;
            ss << f.rdbuf(); // reading data
            str = ss.str();
            return str.size();
        }
        f.close();
    }
    cout<<"NO FILE FOUND"<<endl;
    return -1;

}

void reconstruct_file(int k,int parts,u8** frag_ptrs){
	
    cout<<"WRITE RECONSTRUCT FILE"<<endl;
    string reconstructed_message = "";
	int lrow_count =0;
	while(lrow_count<parts && frag_ptrs[k-1][lrow_count]!='\0')
			lrow_count++;

	// cout<<"LAST ROW COUNT "<<lrow_count<<endl;
	string main_extension = "";
    string main_filename = "hexdump";
    string filename = main_filename+"_reconstruct"+main_extension;
    ofstream outfile(filename, ios::out | ios::binary);

    const char *array = reconstructed_message.c_str();
    for(int i=0;i<(k-1);i++)
        outfile.write((char*) frag_ptrs[i],parts);

	outfile.write((char*) frag_ptrs[k-1],lrow_count); 

    outfile.close();
}


std::string format_duration( std::chrono::microseconds ms ) {
    using namespace std::chrono;
    auto secs = duration_cast<seconds>(ms);
    ms -= duration_cast<microseconds>(secs);
    auto mins = duration_cast<minutes>(secs);
    secs -= duration_cast<seconds>(mins);
    auto hour = duration_cast<hours>(mins);
    mins -= duration_cast<minutes>(hour);

    std::stringstream ss;
    ss << hour.count() << " Hours : " << mins.count() << " Minutes : " << secs.count() << " Seconds : " << ms.count() << " Microseconds";
    return ss.str();
}

int main(int argc, char *argv[]){

	int k = 6, r = 2;
    int n = k+r;
    int l = 2; // Number of local groups

	int nerrs;

    // Get starting timepoint
    auto start = high_resolution_clock::now();

	// Fragment buffer pointers
	u8 *frag_ptrs[MMAX];
	u8 *recover_srcs[KMAX];
	u8 *recover_outp[KMAX];
	vector<int> frag_err_list;
	vector<int> frag_present_list;

    int i;
    string main_extension = "";
    string main_filename = "hexdump";
    cout<<"MAIN FILENAME "<<main_filename<<endl;

	printf("ec_simple_example:\n");
    int parts = file_size(n);
    cout<<"PARTS : "<<parts<<endl;

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
			frag_present_list.push_back(i);
        } else{
			frag_err_list.push_back(i);
            for(int j=0;j<parts;j++){
                frag_ptrs[i][j] = 0;
            }
        }
    }

    int j;

	frag_err_list = decode_local_groups(n, k, r, l, parts,frag_present_list,frag_err_list,frag_ptrs);
	cout<<endl;
	// cout<<endl;
    // for (i = 0; i < n; i++){
	// 	for (j = 0; j < 20; j++){
    //         cout<<(int) frag_ptrs[i][j]<<" ";
    //     }
    //     cout<<endl;
    // }
    // cout<<endl;

	nerrs = frag_err_list.size();
	sort(frag_err_list.begin(),frag_err_list.end());
	
	int src_errs = 0;

	for(auto it:frag_err_list)
		if(it < k)
			src_errs++;
		
	cout<<"Number of errors "<<nerrs<<endl;
	cout<<"Number of source errors "<<src_errs<<endl;
	cout<<endl;


	if (src_errs > 0) {
		if(src_errs > r) {
			cout<<"NOT DECODABLE"<<endl;
			return -1;
		} else {
			for(i=0;i<src_errs;i++)
				printf("Error at postition - %d\n",frag_err_list[i]);
		
			decode_data(n,k, r, parts,frag_err_list,frag_ptrs,recover_srcs,recover_outp);

			for (i = 0; i < n; i++){
				for (j = 0; j < 20; j++){
					cout<<(int) frag_ptrs[i][j]<<" ";
				}
				cout<<endl;
			// cout<<convertToString(frag_ptrs[i],parts)<<endl;
			}
			cout<<endl;
		}
	}
	reconstruct_file(k,parts,frag_ptrs);
	cout<<endl;
	// Get ending timepoint
    auto stop = high_resolution_clock::now();
  
    // Get duration. Substart timepoints to 
    // get durarion. To cast it to proper unit
    // use duration cast method
    auto duration = duration_cast<microseconds>(stop - start);

    cout << "Time taken by function: "
         << format_duration(duration_cast<std::chrono::microseconds>(stop - start)) << endl;
	
    exit(0);
}


