#include<iostream>
#include<string>
#include<cstring>
#include<fstream>
#include<sstream>

typedef unsigned char u8;

using namespace std;

char* readFileBytes(string name,int *length)
{
    ifstream f(name,  ios::in | ios::binary ); //taking file as inputstream
    string str;
    if(f) {
        ostringstream ss;
        ss << f.rdbuf(); // reading data
        str = ss.str();
    }
    f.close();

    char *ret;
    ret = (char*) malloc(str.size()+1);
    for(int i=0;i<str.size();i++)
        ret[i] = str[i];

    *length = str.size();
    cout<<*length<<endl;

    return ret;
}


int main(int argc, char *argv[]){

    string filename = "LDC.pdf";
    int length;
    u8* file = (u8*) readFileBytes(filename,&length);

    string name = "";
    string ext = "";
    int curr_pos = 0;
    while(curr_pos != filename.size()){
        if(filename[curr_pos] == '.'){
            curr_pos++;
            break;
        }
        name.push_back(filename[curr_pos]);
        curr_pos++;
    }
    while(curr_pos != filename.size()){
        ext.push_back(filename[curr_pos]);
        curr_pos++;
    }
    cout<<"NAME - "<<name<<endl;
    cout<<"EXT - "<<ext<<endl;

    // int length = sizeof(file)/sizeof(char);//sizeof char is guaranteed 1, so sizeof(a) is enough
    cout<<length<<endl;
    // cout<<strlen(file)<<endl;
 
    filename = "LDC2.pdf";
    ofstream outfile(filename,ios::out | ios::binary);
    outfile.write((char*) file,length);        
    outfile.close();
    
    free(file);

    exit(0);
}
