#include <cstddef>
#include <iostream>
#include <string>
#include<fstream>
#include<sstream>
#include <utility>
#include<stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <bitset>

#include "schifra/schifra_galois_field.hpp"
#include "schifra/schifra_galois_field_polynomial.hpp"
#include "schifra/schifra_sequential_root_generator_polynomial_creator.hpp"
#include "schifra/schifra_reed_solomon_encoder.hpp"
#include "schifra/schifra_reed_solomon_block.hpp"
#include "schifra/schifra_error_processes.hpp"

using namespace std;

string convertToString(char* a)
{
    int i;
    int size = sizeof(a)/sizeof(char);
    string s = "";
    for (i = 0; i < size; i++) {
        s = s + a[i];
    }
    return s;
}

string xor_strings(string s1,string s2){
    string result = "";
    result.resize(s1.size(),0x00);
    for(int i=0;i<s1.size();i++)
        result[i] = s1[i] ^ s2[i];

    return result;
}


string local_block(vector<string> local_group){
    string result = xor_strings(local_group[0],local_group[1]);

    for(int i=2;i<local_group.size();i++){
        result = xor_strings(local_group[i] , result);
    }
    return result;
}

int main(int argc, char *argv[]){

    /* Finite Field Parameters */
    const std::size_t field_descriptor                =   8;
    const std::size_t generator_polynomial_index      = 120;
    const std::size_t generator_polynomial_root_count =  20;

    /* Reed Solomon Code Parameters */
    const std::size_t code_length = 255;
    const std::size_t fec_length  =  20;
    const std::size_t data_length = code_length - fec_length;

    // /* Finite Field Parameters */
    // const std::size_t field_descriptor                = 4;
    // const std::size_t generator_polynomial_index      = 2;
    // const std::size_t generator_polynomial_root_count = 3;

    // /* Reed Solomon Code Parameters */
    // const std::size_t code_length = 15;
    // const std::size_t fec_length  =  3;
    // const std::size_t data_length = code_length - fec_length;
    
    int l = 3; // Number of local groups

    /* Instantiate Finite Field and Generator Polynomials */
    const schifra::galois::field field(field_descriptor,
                                        schifra::galois::primitive_polynomial_size06,
                                        schifra::galois::primitive_polynomial06);

    schifra::galois::field_polynomial generator_polynomial(field);

    if (
        !schifra::make_sequential_root_generator_polynomial(field,
                                                            generator_polynomial_index,
                                                            generator_polynomial_root_count,
                                                            generator_polynomial)
        )
    {
        std::cout << "Error - Failed to create sequential root generator!" << std::endl;
        return 1;
    }

    /* Instantiate Encoder and Decoder (Codec) */
    typedef schifra::reed_solomon::encoder<code_length,fec_length,data_length> encoder_t;

    const encoder_t encoder(field, generator_polynomial);

    // char file[]= "";
    // sscanf(argv[1], "%s", file);
    // if(file == ""){
    //     cout<<"ENTER FILE NAME"<<endl;
    //     return 1;
    // }
    // cout<<file<<endl;

    // string main_filename = convertToString(file);
    // cout<<"MAIN FILENAME "<<main_filename<<endl;

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

    int parts = (str.length()/data_length);
    if(str.length()%data_length){
        parts +=1;
    }

    cout<<"CHUNK SIZE : "<<parts<<endl;

    string full_encode = "";
    string tmp = "";
    tmp.resize(fec_length,0x00);


    for(int i=0;i<parts;i++){

        std::string message = str.substr(i*data_length,data_length);

        /* Instantiate RS Block For Codec */
        schifra::reed_solomon::block<code_length,fec_length> block;
        
        message.resize(data_length,0x00);

        /* Transform message into Reed-Solomon encoded codeword */
        if (!encoder.encode(message, block))
        {
            std::cout << "Error - Critical encoding failure! "
                    << "Msg: " << block.error_as_string()  << std::endl;
            return 1;
        }

        block.fec_to_string(tmp);

        full_encode += (message+tmp);
    }

    cout<<"WRITE FILES"<<endl;
    cout<<code_length<<endl;
    
    // Make the folder for parts
    mkdir("parts", 0777);

    for(int i=0;i<code_length;i++){
        tmp = "";
        for(int j=0;j<parts;j++){
            tmp += full_encode[i+j*code_length];
        }

        string filename = "parts/myfile_"+to_string(i+1);
        ofstream outfile(filename,ios::out | ios::binary);
        outfile.write(tmp.c_str(),tmp.size());        
        outfile.close();
    }
    
    // GENERATING LRC BLOCK CODES
    for(int i=0;i<l;i++){
        vector<string> local_group;
        
        for(int j=0;j<data_length/l;j++){
            string tmp="";
            for(int k=0;k<parts;k++){
                tmp += full_encode[i*(data_length/l)+j+k*data_length];
            }
            local_group.push_back(tmp);
            // cout<<tmp<<endl;
        }

        string result = local_block(local_group);

        string filename = "parts/myfile_local_"+to_string(i+1);
        ofstream outfile(filename,ios::out | ios::binary);
        outfile.write(result.c_str(),result.size());        
        outfile.close();
    }

    exit(0);
}
