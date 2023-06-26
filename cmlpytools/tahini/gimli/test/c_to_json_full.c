#include <stdint.h>
#include <stdlib.h>

#include "c_to_json_full.h"

enum RAY RAY;

enum THREAD THREAD;

// @regmap brief: "A deer, a female deer"
// @regmap address: 1024
uint16_t doe;

// @regmap brief: "A drop of golden sun"
// @regmap address: 2048
// @regmap value_enum: "RAY"
uint16_t ray;

// @regmap brief: "A name I call myself"
// @regmap address: 3072
uint16_t me[3];

// @regmap brief: "A long long way to run"
// @regmap address: 4096
// @regmap visibility: "PRIVATE"
struct far far;

// @regmap brief: "A needle pulling a thread"
// @regmap address: 5120
union sew sew;

// @regmap brief: "A note to follow so"
// @regmap address: 6144
union la la;

// @regmap brief: "A drink with jam and bread"
// @regmap address: 7168
struct tea tea;

int main(void)
{
	return EXIT_SUCCESS;
}
