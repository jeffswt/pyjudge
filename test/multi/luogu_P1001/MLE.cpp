#include <iostream>
#include <vector>
using namespace std;
vector<char> vec;
int a, b;
int main() {
	vec.resize(1024 * 1024 * 1024);
	cin >> a >> b;
	cout << a + b << endl;
	return 0;
}