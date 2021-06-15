#include<cstddef>
#include<iostream>
#include<string>
#include<fstream>
#include<sstream>

#include "schifra/schifra_galois_field.hpp"
#include "schifra/schifra_galois_field_polynomial.hpp"
#include "schifra/schifra_sequential_root_generator_polynomial_creator.hpp"
#include "schifra/schifra_reed_solomon_encoder.hpp"
#include "schifra/schifra_reed_solomon_decoder.hpp"
#include "schifra/schifra_reed_solomon_block.hpp"
#include "schifra/schifra_error_processes.hpp"

using namespace std;

int main()
{
   /* Finite Field Parameters */
   const std::size_t field_descriptor                =   8;
   const std::size_t generator_polynomial_index      = 120;
   const std::size_t generator_polynomial_root_count =  32;

   /* Reed Solomon Code Parameters */
   const std::size_t code_length = 255;
   const std::size_t fec_length  =  32;
   const std::size_t data_length = code_length - fec_length;

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
   typedef schifra::reed_solomon::decoder<code_length,fec_length,data_length> decoder_t;

   const encoder_t encoder(field, generator_polynomial);
   const decoder_t decoder(field, generator_polynomial_index);

   string main_filename = "hexdump";
   string main_extension = "";
   ifstream f(main_filename+main_extension,  ios::in | ios::binary ); //taking file as inputstream
   string str;
   if(f) {
      ostringstream ss;
      ss << f.rdbuf(); // reading data
      str = ss.str();
   }
   f.close();
   // cout<<str<<endl;
   cout<<str.length()<<endl;

   int parts = (str.length()/data_length);
   if(str.length()%data_length){
      parts +=1;
   }

   cout<<parts<<endl;

   string remade_file = "";
   string full_encode = "";

   for(int i=0;i<parts;i++){
   
   std::string message = str.substr(i*data_length,data_length);
   // std::string message = "An expert is someone who knows more and more about less and "
   //                       "less until they know absolutely everything about ";

   // std::cout << "Original Message (BEFORE PADDING):  [" << message << "] Size: " <<message.size()<<std::endl;
   /* Pad message with nulls up until the data-word length */
   cout<<message.size()<<endl;
   message.resize(data_length,0x00);
   cout<<message.size()<<endl;
   // std::cout << "Original Message (AFTER PADDING):  [" << message << "] Size: " <<message.size()<<std::endl;

   /* Instantiate RS Block For Codec */
   schifra::reed_solomon::block<code_length,fec_length> block;

   /* Transform message into Reed-Solomon encoded codeword */
   if (!encoder.encode(message, block))
   {
      std::cout << "Error - Critical encoding failure! "
                << "Msg: " << block.error_as_string()  << std::endl;
      return 1;
   }

   string tmp = "";
   tmp.resize(fec_length,0x00);
   block.fec_to_string(tmp);
   // cout<<tmp<<endl;

   full_encode += (message+tmp);

   // std::cout << "Encoded Codeword: [" << block << "]" << std::endl;

   /* Add errors at every 3rd location starting at position zero */
   // schifra::corrupt_message_all_errors00(block, 0, 6);

   // // std::cout << "Corrupted Codeword: [" << block << "]" << std::endl;

   // if (!decoder.decode(block))
   // {
   //    std::cout << "Error - Critical decoding failure! "
   //              << "Msg: " << block.error_as_string()  << std::endl;
   //    return 1;
   // }
   // else if (!schifra::is_block_equivelent(block, message))
   // {
   //    std::cout << "Error - Error correction failed!" << std::endl;
   //    return 1;
   // }

   // block.data_to_string(message);

   // message.erase(find(message.begin(), message.end(), '\0'), message.end());
   

   // std::cout << "Corrected Message: [" << message << "]" << std::endl;
   // remade_file += message;
   // cout<<endl;
   // cout<<endl;
   }
   // cout<<"remade_file"<<endl;
   cout<<"Size: "<<full_encode.size()<<endl;
   // cout<<full_encode<<" Size: "<<full_encode.size()<<endl;
   // cout<<endl;

   cout<<"WRITE FILES"<<endl;
   for(int i=0;i<code_length;i++){
      string tmp="";
      for(int j=0;j<parts;j++){
         tmp += full_encode[i+j*code_length];
      }
      // cout<<i<<" "<<tmp<<endl;

      string filename = "parts/myfile_"+to_string(i+1);
        // filename += ".bin"; 
        // cout<<filename<<endl;
        ofstream outfile(filename, ofstream::binary);
        outfile << tmp;
        
        outfile.close();
   }

   string read_file = "";
   read_file.resize(parts*code_length,0x00);

   cout<<"READ FILES"<<endl;
    for(int i=0;i<code_length;i++){
      //   if(i==2 || i==7 || i==10 || i==13 || i==1) continue;
      //   if(i == 2) continue;
        string filename = "parts/myfile_"+to_string(i+1);
        // filename += ".bin"; 
        ifstream f(filename, ifstream::binary); //taking file as inputstream
        string str;
        // cout<<filename<<endl;
        if(f) {
            ostringstream ss;
            ss << f.rdbuf(); // reading data
            str = ss.str();
        }

        f.close();
         for(int j=0;j<parts;j++){
            read_file[i+j*code_length] = str[j];
         }

    }
   // cout<<read_file<<" Size: "<<read_file.size()<<endl;
   // cout<<endl;
   // cout<<endl;
   // cout<<endl;
   // cout<<endl;
   string reconstructed_message = "";
   for(int i=0;i<parts;i++){
      string part = read_file.substr(i*code_length,code_length);
      schifra::reed_solomon::block<code_length,fec_length> block(part.substr(0,data_length),part.substr(data_length,fec_length));

      string decoded_message = "";
      decoded_message.resize(data_length,0x00);

      block.data_to_string(decoded_message);
      // cout<<decoded_message<<" "<<decoded_message.size()<<endl;

      if (!decoder.decode(block))
      {
         std::cout << "Error - Critical decoding failure! "
                  << "Msg: " << block.error_as_string()  << std::endl;
         return 1;
      }
      else if (!schifra::is_block_equivelent(block, decoded_message))
      {
         std::cout << "Error - Error correction failed!" << std::endl;
         return 1;
      }

      block.data_to_string(decoded_message);

      decoded_message.erase(find(decoded_message.begin(), decoded_message.end(), '\0'), decoded_message.end());
      // cout<<decoded_message<<" "<<decoded_message.size()<<endl;

      reconstructed_message +=decoded_message;

   }

   // cout<<reconstructed_message<<endl<<"Size: "<<reconstructed_message.size()<<endl;

   string filename = main_filename+"_reconstruct"+main_extension;
   // filename += ".bin"; 
   // cout<<filename<<endl;
   ofstream outfile(filename, ios::out | ios::binary);
   // outfile << reconstructed_message;
   const char *array = reconstructed_message.c_str();
   outfile.write(array,reconstructed_message.size());
   outfile.close();

   std::cout << "Encoder Parameters [" << encoder_t::trait::code_length << ","
                                       << encoder_t::trait::data_length << ","
                                       << encoder_t::trait::fec_length  << "]" << std::endl;

   std::cout << "Decoder Parameters [" << decoder_t::trait::code_length << ","
                                       << decoder_t::trait::data_length << ","
                                       << decoder_t::trait::fec_length  << "]" << std::endl;


   return 0;
}
