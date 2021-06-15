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

int main(int argc, char *argv[])
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

   int parts;

   string tmp = "parts/myfile_"+to_string(1);
   ifstream f(tmp, ifstream::binary); //taking file as inputstream
   string str;
   // cout<<tmp<<endl;
   if(f) {
      ostringstream ss;
      ss << f.rdbuf(); // reading data
      str = ss.str();
   }
   f.close();
   parts = str.size();

   cout<<"READ FILES"<<endl;
   string read_file = "";
   read_file.resize(parts*code_length,0x00);

    for(int i=0;i<code_length;i++){
        // if(i==2 || i==7 || i==10 || i==13 || i==1) continue;
        // if(i<7) continue;
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
   cout<<read_file<<endl<<"Size: "<<read_file.size()<<endl;
   cout<<endl;
   cout<<endl;
   cout<<endl;
   cout<<endl;
   string reconstructed_message = "";
   for(int i=0;i<parts;i++){
      string part = read_file.substr(i*code_length,code_length);
      schifra::reed_solomon::block<code_length,fec_length> block(part.substr(0,data_length),part.substr(data_length,fec_length));

      string decoded_message = "";
      decoded_message.resize(data_length,0x00);

      block.data_to_string(decoded_message);

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
    
      reconstructed_message +=decoded_message;

   }

   cout<<reconstructed_message<<endl<<"Size: "<<reconstructed_message.size()<<endl;


   return 0;
}
