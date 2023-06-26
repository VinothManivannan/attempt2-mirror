#ifndef PLATFORM_SPECIFIC_HEADER_H
#define PLATFORM_SPECIFIC_HEADER_H

enum RAY {
    RAY_OFF = 0,
    RAY_LOW = 1,
    RAY_MID = 2,
    RAY_HIGH = 3
};

enum THREAD {
    RED,
    GREEN,
    BLUE
};

struct far {
    // @regmap brief: "Distance to get it"
    uint16_t fetched;

    // @regmap brief: "Distance to see it"
    int32_t sighted;
};

union sew {
    
    // @regmap brief: "Thread count by index"
    // @regmap array_enum: "THREAD"
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

#endif
