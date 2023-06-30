#include <stdint.h>
#include <stdlib.h>

union la {
    // @regmap brief: "All notes"
    uint8_t notes;

    // @regmap brief: "Each note"
    struct {
        uint8_t A : 1;
        uint8_t B : 1;
        uint8_t C : 1;
        uint8_t D : 1;
        uint8_t E : 1;
        uint8_t F : 1;
        uint8_t G : 1;
    } note;
};

// @regmap brief: "A note to follow so"
// @regmap address: 6144
volatile union la la;

int main(void)
{
	return EXIT_SUCCESS;
}
