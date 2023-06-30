#include <stdint.h>
#include <stdlib.h>

enum THREAD {
    RED,
    GREEN,
    BLUE
};

volatile enum THREAD THREAD;

union sew {
    // @regmap brief: "Thread count by index"
    // @regmap array_enum: THREAD
    uint16_t threads[3];

    // @regmap brief: "Thread count by name"
    struct {

        // @regmap brief: "Number of red threads"
        uint8_t red;
        
        uint8_t _reserved0;
        
        // @regmap brief: "Number of green threads"
        uint8_t green;
        
        uint8_t _reserved1;
        
        // @regmap brief: "Number of blue threads"
        uint8_t blue;
        
        uint8_t _reserved2;
        
    } thread;
};

// @regmap brief "A needle pulling a thread"
// @regmap address 5120
volatile union sew sew;

int main(void)
{
	return EXIT_SUCCESS;
}
