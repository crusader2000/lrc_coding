#include<cstddef>
#include<iostream>
#include<string>
#include<fstream>
#include<sstream>

#include "schifra/schifra_galois_field.hpp"
#include "schifra/schifra_galois_field_polynomial.hpp"
#include "schifra/schifra_sequential_root_generator_polynomial_creator.hpp"
#include "schifra/schifra_reed_solomon_decoder.hpp"
#include "schifra/schifra_reed_solomon_block.hpp"
#include "schifra/schifra_error_processes.hpp"

using namespace std;

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

int main()
{
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
    // const std::size_t generator_polynomial_index      = 1;
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
    typedef schifra::reed_solomon::decoder<code_length,fec_length,data_length> decoder_t;

    const decoder_t decoder(field, generator_polynomial_index);

    string main_filename = "hexdump";
    string main_extension = "";


    ifstream f(main_filename+main_extension,  ios::in | ios::binary ); //taking file as inputstream
    string str_main;
    if(f) {
        ostringstream ss;
        ss << f.rdbuf(); // reading data
        str_main = ss.str();
    }
    f.close();

    int num_global_files_not_present = 0;
    int num_local_files_not_present = 0;

    for(int i=0;i<code_length;i++){
        string filename = "parts/myfile_"+to_string(i+1);
        ifstream f(filename);
        if(f.fail()){
            num_global_files_not_present++;
        }
        f.close();
    }


    for(int i=0;i<l;i++){
        string filename = "parts/myfile_local_"+to_string(i+1);
        ifstream f(filename);
        if(f.fail()){
            num_local_files_not_present++;
        }
        f.close();
    }

    cout<<"NUMBER OF GLOBAL FILE NOT PRESENT "<<num_global_files_not_present<<endl;
    cout<<"NUMBER OF LOCAL FILE NOT PRESENT "<<num_local_files_not_present<<endl;

    int parts = file_size(code_length);
    string read_file = "";
    read_file.resize(parts*code_length,0x00);
    
    schifra::reed_solomon::erasure_locations_t locations;
    

    cout<<"READ FILES"<<endl;
    for(int i=0;i<code_length;i++){
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
                read_file[i+j*code_length] = str[j];
            }
        } else{
            locations.push_back(i);
        }
    }
    cout<<"LOCATIONS MISSING "<<locations.size()<<endl;
    for(auto it:locations)
        cout<<it<<endl;

    // for(int i=0;i<l;i++){
    //     vector<int> parts_missing;
    //     for(auto it:locations){
    //         if(it>=i*(data_length/l) && it<(i+1)*(data_length/l)){
    //             parts_missing.push_back(it);
    //         }
    //     }
    //     string filename = "parts/myfile_local_"+to_string(i+1);
    //     ifstream f(filename);
    //     if(parts_missing.size() == 1 && f){
    //         regenerate_part(read_file,parts_missing[0]);
    //     }

    // }
    // cout<<read_file<<endl;
    
    cout<<"DECODE FILES"<<endl;
    string reconstructed_message = "";
    for(int i=0;i<parts;i++){
        string part = read_file.substr(i*code_length,code_length);
        schifra::reed_solomon::block<code_length,fec_length> block(part.substr(0,data_length),part.substr(data_length,fec_length));

        // part = str_main.substr(i*data_length,data_length);
        // cout<<part<<" "<<part.size()<<endl;
        // for(auto it:part)
        //     cout<<(int) it<<" ";
        // cout<<endl;
        
        string decoded_message = "";
        decoded_message.resize(data_length,0x00);
        // block.data_to_string(decoded_message);
        // cout<<decoded_message<<" "<<decoded_message.size()<<endl;
        // for(auto it:decoded_message)
        //     cout<<(int) it<<" ";
        // cout<<endl;
        if (!decoder.decode(block,locations))
        {
            std::cout <<i<<"Error - Critical decoding failure! "
                    << "Msg: " << block.error_as_string()  << std::endl;
            // return 1;
        }

        block.data_to_string(decoded_message);
        
        // decoded_message.erase(find(decoded_message.begin(), decoded_message.end(), 0x00), decoded_message.end());
        decoded_message.erase(find(decoded_message.begin(), decoded_message.end(), '\0'), decoded_message.end());
        
        // cout<<decoded_message<<" "<<decoded_message.size()<<endl;
        // for(auto it:decoded_message)
        //     cout<<(int) it<<" ";
        // cout<<endl;
        // cout<<"----------------------"<<endl;
        reconstructed_message +=decoded_message;
        // cout<<decoded_message<<endl;
    }


    // ///////////////////////////////
    // LOCAL GROUP MISSING
    // ///////////////////////////////
    cout<<"WRITE RECONSTRUCT FILE"<<endl;
    string filename = main_filename+"_reconstruct"+main_extension;
    ofstream outfile(filename, ios::out | ios::binary);
    const char *array = reconstructed_message.c_str();
    outfile.write(array,reconstructed_message.size());
    outfile.close();

    return 0;
}
