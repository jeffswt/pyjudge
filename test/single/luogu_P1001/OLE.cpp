#include <iostream>
using namespace std;
int main() {
	int x = 0;
	while(1) putchar('0' + (x++)), x %= 10;
	return 0;
}