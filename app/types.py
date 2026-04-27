from enum import Enum


class Goal(str, Enum):
    FAT_LOSS = "fat_loss"
    MAINTENANCE = "maintenance"
    MUSCLE_GAIN = "muscle_gain"
    RECOMPOSITION = "recomposition"


class DietType(str, Enum):
    VEG = "veg"
    EGGETARIAN = "eggetarian"
    NON_VEG = "non_veg"
    VEGAN = "vegan"