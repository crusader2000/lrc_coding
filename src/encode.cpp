#include<iostream>
#include<string>
#include<fstream>
#include<sstream>
#include<sys/stat.h>
#include<vector>

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <isa-l.h>	
// #include "../libs/isa-l/isa-l.h"	// use <isa-l.h> instead when linking against installed
// #include "../libs/isa-l/include/erasure_code.h"
// #include "../libs/isa-l/include/crc.h"
// #include "../libs/isa-l/include/crc64.h"
// #include "../libs/isa-l/include/gf_vect_mul.h"
// #include "../libs/isa-l/include/igzip_lib.h"
// #include "../libs/isa-l/include/raid.h"

#define MMAX 255
#define KMAX 255

typedef unsigned char u8;

using namespace std;

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


    string main_extension = "";
    string main_filename = "hexdump";
    cout<<"MAIN FILENAME "<<main_filename<<endl;

    ifstream f(main_filename+main_extension,  ios::in | ios::binary ); //taking file as inputstream
    string str;
    if(f) {
        ostringstream ss;
        ss << f.rdbuf(); // reading data
        str = ss.str();
    }
    f.close();

    // cout<<str<<endl;
    cout<<"FILESIZE : "<<str.length()<<endl;

    int parts; 

    if(!(str.length()%k)){
        parts = str.length()/k;
    } else{
        parts = ((int) str.length()/k) + 1;
        // cout<<str.size()<<endl;
        str.resize(parts*k,0x00);
        // cout<<str.size()<<endl;
        // for(int j=0;j<parts;j++)
        //     cout<<(k-1)*parts+j<<" "<<(int) str[(k-1)*parts+j]<<endl;
        // cout<<endl;
            
    }
    cout<<"FILESIZE : "<<str.length()<<endl;
    cout<<"PARTS : "<<parts<<endl;
    int i;
    for (i = 0; i < r; i++)
        frag_err_list[nerrs++] = rand() % (k + r);


	printf("ec_simple_example:\n");

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

    int j;
	// Fill sources with DATA
	for (i = 0; i < k; i++){
		for (j = 0; j < parts; j++){
			frag_ptrs[i][j] = (u8) str[j+parts*i];
            // cout<<frag_ptrs[i][j]<<" "<<str[j+parts*i]<<endl;
        }
        // cout<<convertToString(frag_ptrs[i],parts)<<endl;
    }
    for (i = 0; i < k; i++){
		for (j = 0; j < 20; j++){
            cout<<(int) frag_ptrs[i][j]<<" ";
        }
        cout<<endl;
       // cout<<convertToString(frag_ptrs[i],parts)<<endl;
    }

    cout<<endl;
	printf(" encode (n,k,r)=(%d,%d,%d) len=%d\n", n, k, r, parts);
    cout<<endl;

	// Pick an encode matrix. A Cauchy matrix is a good choice as even
	// large k are always invertable keeping the recovery rule simple.
	gf_gen_cauchy1_matrix(encode_matrix, n, k);

	// Initialize g_tbls from encode matrix
	ec_init_tables(k, r, &encode_matrix[k * k], g_tbls);

	// Generate EC parity blocks from sources
	ec_encode_data(parts, k, r, g_tbls, frag_ptrs, &frag_ptrs[k]);

	for (i = 0; i < n; i++){
		for (j = 0; j < 20; j++){
            cout<<(int) frag_ptrs[i][j]<<" ";
        }
        cout<<endl;
    }

    // Make the folder for parts
	printf("\nWRITING FILES\n");
    mkdir("parts", 0777);

    for(int i=0;i<n;i++){

        string tmp = convertToString(frag_ptrs[i],parts);

        string filename = "parts/myfile_"+to_string(i+1);
        ofstream outfile(filename,ios::out | ios::binary);
        outfile.write(tmp.c_str(),tmp.size());        
        outfile.close();
    }
    
    // // GENERATING LRC BLOCK CODES
    // for(int i=0;i<l;i++){
    //     vector<string> local_group;
        
    //     for(int j=0;j<data_length/l;j++){
    //         string tmp="";
    //         for(int k=0;k<parts;k++){
    //             tmp += full_encode[i*(data_length/l)+j+k*data_length];
    //         }
    //         local_group.push_back(tmp);
    //         // cout<<tmp<<endl;
    //     }

    //     string result = local_block(local_group);

    //     string filename = "parts/myfile_local_"+to_string(i+1);
    //     ofstream outfile(filename,ios::out | ios::binary);
    //     outfile.write(result.c_str(),result.size());        
    //     outfile.close();
    // }

    exit(0);
}
