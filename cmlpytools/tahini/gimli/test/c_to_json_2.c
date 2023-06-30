#include <stdint.h>
#include <stdlib.h>

enum RAY {
    // @regmap brief: "The ray is off"
    RAY_OFF = 0,
    // @regmap brief: "The ray is low"
    RAY_LOW=1,
    // @regmap brief: "The ray is mid"
    RAY_MID,
    // @regmap brief: "The ray is high"
    RAY_HIGH
};

// @regmap brief: "The ray enum"
volatile enum RAY RAY;

// @regmap brief: "A drop of golden sun"
// @regmap address: 2048
// @regmap value_enum: "RAY"
volatile uint16_t ray;

int main(void)
{
	return EXIT_SUCCESS;
}
