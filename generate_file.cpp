#include <iostream>
#include <fstream>
#include <string>
#include <vector>
using namespace std;

int main() {
    ofstream file("hello.txt");
    for (long long i = 0; i < 100000000; i++) {
        string line = to_string(i + 1);
        line.append(" timur 1 timur 2 timur 3 timur 4 timur 5 timur 6 timur 7 DONT STOP THIS MAN!\n");
        file << line;
    }
    file.close();
}

