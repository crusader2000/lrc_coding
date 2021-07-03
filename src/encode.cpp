#include<iostream>
#include<string>
#include<fstream>
#include<sstream>
#include<sys/stat.h>
#include<vector>
#include <chrono>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <isa-l.h>	

#define MMAX 255
#define KMAX 255

typedef unsigned char u8;

using namespace std;
using namespace std::chrono;

char* readFileBytes(const char *name)
{
    ifstream fl(name);
    fl.seekg( 0, ios::end );
    size_t len = fl.tellg();
    char *ret = new char[len];
    fl.seekg(0, ios::beg); 
    fl.read(ret, len);
    fl.close();
    return ret;
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

	int nerrs = 0;

    // Get starting timepoint
    auto start = high_resolution_clock::now();

	// Fragment buffer pointers
	u8 *frag_ptrs[MMAX];

	// Coefficient matrices
	u8 *encode_matrix;
    u8 *g_tbls;


    string name;
    name = string(argv[1]);
    cout<<"FILENAME : "<<name<<endl;

    ifstream f("hexdump",  ios::in | ios::binary ); //taking file as inputstream
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

	printf("ec_simple_example:\n");

	// Allocate coding matrices
	encode_matrix = (u8*) malloc(n * k);

	g_tbls = (u8*) malloc(k * r * 32);

    if (encode_matrix == NULL || g_tbls == NULL) {
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

        // string tmp = convertToString(frag_ptrs[i],parts);

        string filename = "parts/"+name+"_"+to_string(i+1);
        ofstream outfile(filename,ios::out | ios::binary);
        outfile.write((char*) frag_ptrs[i],parts);        
        outfile.close();
    }
        // cout<<endl;     
        // cout<<endl;     
    
    
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
