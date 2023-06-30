#include <stdint.h>
#include <stdlib.h>

struct tea {
    struct {
        // @regmap brief: "Consumption %age - popularity"   
        uint8_t consumption;
        
        // @regmap brief: "Oxidation level"   
        uint8_t oxidation;
        
        struct {
            // @regmap brief: "Consume with milk"  
            uint8_t with_milk : 1;
            
            // @regmap brief: "Consume with lemon"  
            uint8_t with_lemon : 1;
        } consume;
    } black, green, oolong, white, pu_erh;
};

// @regmap brief: "A drink with jam and bread"
// @regmap address: 7168
volatile struct tea tea;

int main(void)
{
	return EXIT_SUCCESS;
}
