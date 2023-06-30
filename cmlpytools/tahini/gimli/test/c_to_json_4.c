#include <stdint.h>
#include <stdlib.h>

struct far {
    // @regmap brief: "Distance to get it"
    uint16_t fetched;

    // @regmap brief: "Distance to see it"
    int32_t sighted;
};

// @regmap brief: "A long long way to run"
// @regmap address: 16384
// @regmap access: "private"
// @regmap hif_access: true
volatile struct far far;

int main(void)
{
	return EXIT_SUCCESS;
}
