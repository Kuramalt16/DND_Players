

item_dict = {}

mob_dict = {}

character_dict = {}

SECRETS = {}

images = {}

spell_slots = {} # this variable holds unused spell slots, once it's used gets reduced. format: {'1st': 4, '2nd': 3, '3rd': 2, 'Natural Recovery': 2}

short_rest = []
long_rest = []

Read_data_flag = False

score_modifiers = {}
Proficiecy_bonus = 0
spellcasting_ability_mod = 0

d20_img_count = 0
d20_dice_images = []

Special_Flags = {} # check Help.py

consentration = {}

Players_to_Chars = {"Laura": ["New", "Etheria", "Ru`ahala", "Kugel"],"Rokas": ["New", "Conan", "Crocus"],"Simonas": ["New", "Kalabrimbur", "Galandir"],"Rita": ["New"],"Admin": ["New", "GAR"],}

Languages = ["Common", "Elvish", "Thieves Cant", "Dwarvish", "Orcish", "Draconic", "Goblin", "Druidic", "Celestial", "Giant", "Gnomish", "Abyssal", "Infernal", "Sylvan", "Undercommon"]

Skills = {
    "Acrobatics": [0, "DEX"],
    "Animal Handling": [0, "WIS"],
    "Arcana": [0, "INT"],
    "Athletics": [0, "STR"],
    "Deception": [0, "CHA"],
    "History": [0, "INT"],
    "Insight": [0, "WIS"],
    "Intimidation": [0, "CHA"],
    "Investigation": [0, "INT"],
    "Medicine": [0, "WIS"],
    "Nature": [0, "INT"],
    "Perception": [0, "WIS"],
    "Performance": [0, "CHA"],
    "Persuasion": [0, "CHA"],
    "Religion": [0, "INT"],
    "Sleight of Hand": [0, "DEX"],
    "Stealth": [0, "DEX"],
    "Survival": [0, "WIS"],
    # "Thieves' Tools": [0, "TOOL"]
}
char_name = ""

Ability_score_list = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

some_data = {}
chosen_cantrips = {}
chosen_spells = {}

Spell_save_DC = 0
Spell_attack = 0


# Cantrips             |
# Spells               |
# Total_Spell_Slots    |
# Spell_Slot_levels    |
# Highest spell slot   V
Available_spells_data = \
    {
        "Warlock":
            {
                1: [2, 2, 1, "1st:1", 1],
                2: [2, 3, 2, "1st:2", 1],
                3: [2, 4, 2, "2nd:2", 2],
                4: [3, 5, 2, "2nd:2", 2],
                5: [3, 6, 2, "3rd:2", 3]
            },
        "Arcane Trickster":
            {
                3: [3, 3, 2, "1st:2", 1],
                4: [3, 4, 3, "1st:3", 1],
                5: [3, 4, 3, "1st:3", 1],
                6: [3, 4, 3, "1st:3", 1],
                7: [3, 5, 6, "1st:4,2nd:2", 2],
                8: [3, 6, 6, "1st:4,2nd:2", 2],
                9: [3, 6, 6, "1st:4,2nd:2", 2],
                10: [4, 7, 7, "1st:4,2nd:3", 2],
            },
        "Druid":
            {
                1: [2, "WISMOD+lv", 2, "1st:2", 1],
                2: [2, "WISMOD+lv", 3, "1st:3", 1],
                3: [2, "WISMOD+lv", 6, "1st:4,2nd:2", 2],
                4: [3, "WISMOD+lv", 7, "1st:4,2nd:3", 2],
                5: [3, "WISMOD+lv", 9, "1st:4,2nd:3,3rd:2", 3],
                6: [3, "WISMOD+lv", 10, "1st:4,2nd:3,3rd:3", 3]
            },
        "Ranger":
            {
                1: [0, 0, 0, "", 0],
                2: [0, 2, 2, "1st:2", 1],
                3: [0, 3, 3, "1st:3", 1],
                4: [0, 3, 3, "1st:3", 1],
                5: [0, 4, 6, "1st:4,2nd:2", 2],
                6: [0, 4, 6, "1st:4,2nd:2", 2],
            },
        "Paladin":
            {
                1: [0, "CHAMOD+0", 0, "", 0],
                2: [0, "CHAMOD+1", 2, "1st:2", 1],
                3: [0, "CHAMOD+1", 3, "1st:3", 1],
                4: [0, "CHAMOD+2", 3, "1st:3", 1],
                5: [0, "CHAMOD+2", 6, "1st:4,2nd:2", 2],
                6: [0, "CHAMOD+3", 6, "1st:4,2nd:2", 2],
                7: [0, "CHAMOD+3", 7, "1st:4,2nd:3", 2],
                8: [0, "CHAMOD+4", 7, "1st:4,2nd:3", 2],
                9: [0, "CHAMOD+4", 9, "1st:4,2nd:3,3rd:2", 3],
                10: [0, "CHAMOD+5", 9, "1st:4,2nd:3,3rd:2", 3],
                11: [0, "CHAMOD+5", 10, "1st:4,2nd:3,3rd:3", 3],

            },
        "Wizard":
            {
                1: [3, "INTMOD+1", 2, "1st:2", 1],
                2: [3, "INTMOD+2", 3, "1st:3", 1],
                3: [3, "INTMOD+3", 6, "1st:4,2nd:2", 2],
                4: [4, "INTMOD+4", 7, "1st:4,2nd:3", 2],
                5: [4, "INTMOD+5", 9, "1st:4,2nd:3,3rd:2", 3],
                6: [4, "INTMOD+6", 10, "1st:4,2nd:3,3rd:3", 3],
                7: [4, "INTMOD+7", 11, "1st:4,2nd:3,3rd:3,4th:1", 4],
                8: [4, "INTMOD+8", 12, "1st:4,2nd:3,3rd:3,4th:2", 4],
                9: [4, "INTMOD+9", 14, "1st:4,2nd:3,3rd:3,4th:3,5th:1", 5],
                10: [5, "INTMOD+10", 15, "1st:4,2nd:3,3rd:3,4th:3,5th:2", 5],
                11: [5, "INTMOD+11", 16, "1st:4,2nd:3,3rd:3,4th:3,5th:2,6th:1", 6],

            },
        "Sorcerer":
            {
                1: [4, 2, 2, "1st:2", 1],
                2: [4, 3, 3, "1st:3", 1],
                3: [4, 4, 6, "1st:4,2nd:2", 2],
                4: [5, 5, 7, "1st:4,2nd:3", 2],
                5: [5, 6, 9, "1st:4,2nd:3,3rd:2", 3],
                6: [5, 7, 10, "1st:4,2nd:3,3rd:3", 3],
                7: [5, 8, 11, "1st:4,2nd:3,3rd:3,4th:1", 4],
                8: [6, 9, 12, "1st:4,2nd:3,3rd:3,4th:2", 4],
                9: [6, 10, 14, "1st:4,2nd:3,3rd:3,4th:3,5th:1", 5],
                10: [6, 11, 15, "1st:4,2nd:3,3rd:3,4th:3,5th:2", 5],
                11: [6, 12, 16, "1st:4,2nd:3,3rd:3,4th:3,5th:2,6th:1", 6],

            },
     }


race_size = {
    "Dwarf": "Small",
    # "Hill Dwarf": "Small",
    # "Mountain Dwarf": "Small",
    #"Halfling": "Small",
    # "Gnome": "Small",
    "Elf": "Medium",
    # "High Elf": "Medium",
    # "Wood Elf": "Medium",
    "Human": "Medium",
    # "Half-Elf": "Medium",
    # "Orc": "Medium",
    # "Half-Orc": "Medium",
    # "Tiefling": "Medium",
    # "Dragonborn": "Medium",
    "Firbolg": "Medium",
    "Kobold": "Small",
    "Changeling": "Medium",
    "Hobgoblin": "Medium",
}

Reactions = {}
Bonus_actions = {}

Conditions = {
    "Blinded": {
        "Description": "A blinded creature can’t see and automatically fails any ability check that requires sight. \n Attack rolls against the creature have advantage, and the creature’s attack rolls have disadvantage."
    },
    "Charmed": {
        "Description": "A charmed creature can’t attack the charmer or target the charmer with harmful abilities or magical effects. \n The charmer has advantage on any ability check to interact socially with the creature."
    },
    "Deafened": {
        "Description": "A deafened creature can’t hear and automatically fails any ability check that requires hearing."
    },
    "Frightened": {
        "Description": "A frightened creature has disadvantage on ability checks and attack rolls while the source of its fear is within line of sight. \n The creature can’t willingly move closer to the source of its fear."
    },
    "Grappled": {
        "Description": "A grappled creature’s speed becomes 0, and it can’t benefit from any bonus to its speed. \n The condition ends if the grappler is incapacitated. \n The condition also ends if an effect removes the grappled creature from the reach of the grappler or grappling effect, such as when a creature is hurled away by the thunderwave spell."
    },
    "Incapacitated": {
        "Description": "An incapacitated creature can’t take actions or reactions."
    },
    "Invisible": {
        "Description": "An invisible creature is impossible to see without the aid of magic or a special sense. For the purpose of hiding, the creature is heavily obscured. The creature’s location can be detected by any noise it makes or any tracks it leaves. \n Attack rolls against the creature have disadvantage, and the creature’s attack rolls have advantage."
    },
    "Paralyzed": {
        "Description": "A paralyzed creature is incapacitated and can’t move or speak. \n The creature automatically fails Strength and Dexterity saving throws. \n Attack rolls against the creature have advantage. \n Any attack that hits the creature is a critical hit if the attacker is within 5 feet of the creature."
    },
    "Petrified": {
        "Description": "A petrified creature is transformed, along with any nonmagical object it is wearing or carrying, into a solid inanimate substance (usually stone). Its weight increases by a factor of ten, and it ceases aging. \n The creature is incapacitated, can’t move or speak, and is unaware of its surroundings. \n Attack rolls against the creature have advantage. \n The creature automatically fails Strength and Dexterity saving throws. \n The creature has resistance to all damage. \n The creature is immune to poison and disease, although a poison or disease already in its system is suspended, not neutralized."
    },
    "Poisoned": {
        "Description": "A poisoned creature has disadvantage on attack rolls and ability checks."
    },
    "Prone": {
        "Description": "A prone creature’s only movement option is to crawl, unless it stands up and thereby ends the condition. \n The creature has disadvantage on attack rolls. \n An attack roll against the creature has advantage if the attacker is within 5 feet of the creature. Otherwise, the attack roll has disadvantage."
    },
    "Restrained": {
        "Description": "A restrained creature’s speed becomes 0, and it can’t benefit from any bonus to its speed. \n Attack rolls against the creature have advantage, and the creature’s attack rolls have disadvantage. \n The creature has disadvantage on Dexterity saving throws."
    },
    "Stunned": {
        "Description": "A stunned creature is incapacitated, can’t move, and can speak only falteringly. \n The creature automatically fails Strength and Dexterity saving throws. \n Attack rolls against the creature have advantage."
    },
    "Unconscious": {
        "Description": "An unconscious creature is incapacitated, can’t move or speak, and is unaware of its surroundings. \n The creature drops whatever it’s holding and falls prone. \n The creature automatically fails Strength and Dexterity saving throws. \n Attack rolls against the creature have advantage. \n Any attack that hits the creature is a critical hit if the attacker is within 5 feet of the creature."
    },
    "Exhaustion": {
        "Description": "Some special abilities and environmental hazards, such as starvation and the long-term effects of freezing or scorching temperatures, can lead to a special condition called exhaustion. Exhaustion is measured in six levels. An effect can give a creature one or more levels of exhaustion, as specified in the effect’s description. \n 1: Disadvantage on ability checks; \n 2: Speed is halved; \n 3: Disadvantage on attack rolls and saving throws; \n 4: Hit point maximum is halved; \n 5: Speed reduced to 0; \n 6: Death \n If an already exhausted creature suffers another effect that causes exhaustion, its current level of exhaustion increases by the amount specified in the effect’s description. \n A creature suffers the effect of its current level of exhaustion as well as all lower levels. For example, a creature suffering level 2 exhaustion has its speed halved and has disadvantage on ability checks. An effect that removes exhaustion reduces its level as specified in the effect’s description, with all exhaustion effects ending if a creature’s exhaustion level is reduced below 1. \n Finishing a long rest reduces a creature’s exhaustion level by 1, provided that the creature has also ingested some food and drink."
    },
    "Encumbrance": {
        "Description": "An encumbered creature looses 10 ft of speed when carrying more than 5 * STR or weight, but less than 10 * STR of weight"
    },
    "Heavily Encumbered": {
        "Description": "A heavily encumbered creature looses 20 ft of speed when carrying more than 10 * STR of weight and has Disadvantage on all Attack rolls, Saving throws, Skill/Ability checks that use Strength, Dexterity or Constitution."
    },
    "Over Encumbered": {
        "Description": "An Over Encumbered creature's speed becomes 0 and it can not take any action and is vulnerable to all attacks and loses concentration."
    }
}

Actions = {
    "Attack": {
        "Description": "Make a physical attack"
    },
    "Cast a spell": {
        "Description": "Cast any spell or cantrip"
    },
    "Dash": {
        "Description": "Double your walking speed"
    },
    "Disengage": {
        "Description": "We dont use opportunity attacks, but if we did this would avoid it."
    },
    "Dodge": {
        "Description": "Opponents have disadvantage on attack rolls against you"
    },
    "Help": {
        "Description": "Help someone, they get advantage on anything they want to do, describe how you are helping"
    },
    "Hide": {
        "Description": "Gives you the surprised attack benefits and creatures won't target you or do so with disadvantage"
    },
    "Ready": {
        "Description": "Set a trigger, once the trigger happens do something, e.g. when the door opens i want to shoot my bow at whoever enters. once the door opens you shoot using a reaction"
    },
    "Search": {
        "Description": "you spend your time looking for something or making investigations."
    },
    "Use an Object": {
        "Description": "Use an item (excluding potions)"
    },
    "Extra Attack": {
        "Description": "If you have more than one extra attack in your features list you can attack more than once"
    }
}

Other_caviots = {
                     "Turn dynamics":{"Description": "During one round which is aprox 6 sec. you can: \n 1: walk up to your speed; \n 2: Use an Action; \n 3: Use a Bonus Action; \n 4: Use a Reaction;"},
                     "Reactions": {"Description": "A Reaction is an action made in response to something."},
                     "Bonus Actions": {"Description": "A Bonus action is basically another Action"},
                     "Two-weapon fighting": {"Description": "When having two weapons in your hands you can make a second attack with your weapon as a bonus action but don't add the modifier on the second attack"},
                     "Shove": {"Description": "If the target is not more than one size larger than you, you can knock it prone or push it 5ft away from you make an Athletics check vs opponents Athletics or Acrobatics check."},
                     "Grapple": {"Description": "If the target is not more than one size larger than you, you can roll Atheltics check vs opponents Athletics or Acrobatics check. If you succeed target has the Grappled Condition, you can end it without an action."},
                     "Fall Damage": {"Description": "When falling you take 1d6 damage per every 10 ft fallen. Up to a maximum of 20d6 \n So fall 100 ft get 10d6 damage. \n You fall at a rate of 500 ft/round"},
                     "Heavy weapons": {"Description": "If the weapon has the Heavy property and you are a small sized creature you have disadvantage on attack rolls with this weapon. Program makes rolls automaticly"},
                     "Concentration break": {"Description": "If you take damage you must roll to see if you keep your concentration or not. the program makes this roll automaticly when taking damage."},
                     "Push, Drag, or Lift": {"Description": "You can push, drag, or lift a weight in pounds up to twice your carrying capacity (or 30 times your Strength score). \n While pushing or dragging weight in excess of your carrying capacity, your speed drops to 5 feet."},
                     "Small letter R on a spell": {"Description": "When you see the small letter R next to a spell it means it is a RITUAL spell."},
                     "Ritual Spells": {"Description": "A ritual spell can be cast following the normal rules for spellcasting, or the spell can be cast as a ritual. \n The ritual version of a spell takes 10 minutes longer to cast than normal. It also doesn’t expend a spell slot, which means the ritual version of a spell can’t be cast at a higher level."}
                }
House_Rules = {
                    "Spell Range:Touch": {"Description": "If range is Touch, means you can Touch yourself, aka spell applies to you as well"},
                    "Throw creature": {"Description": "House Rule: To throw a target you must grapple it and then you can yeet the target (STR score - 10) * (size diferance + 2), e.g. \n Medium creature with 18 STR throws a Large creature, distance will be (18 - 10) * (-1 + 2) = 8 * 1 = 8 ft. \n Medium Throws a small creature will be: (18 - 10) * (1+2) = 8 * 3 = 18 ft"},
                    "Elemental Stuff": {"Description": "Lightning Damage deals more damage to soaked targets, based on targets wetness damage can be multiplied 1.2, 1.5 to a maximum of 2 times as much"},
                    "Rule of cool": {"Description": "If it sounds cool and doesn't completely brake the rules we can do it"}
}

Condition = ""

char_max_hp_tracker = "" # specificly for the exhaustion lv4 condition

spell_effects = {} # effects of spells such as Mage Armour spell

available_subclasses = ["Roguish Archetype", "Patron", "Druid Circle", "Primal Path", "Martial Archetype", "Sacred Oath", "Blood Hunter Order", "Arcane Tradition", "Sorcerous Origin"]
available_classes = ["Barbarian", "Blood Hunter", "Druid", "Fighter", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"]
BASE_SPEED = 0
SPEED_OFFSET = 0

BASE_HIT_DICE = []

BASE_AC = 0

race_size_to_int = {"Tiny": 0,
                    "Small": 1,
                    "Medium": 2,
                    "Large": 3,
                    "Huge": 4,
                    "Gargantuan": 5}

CARRY_TOO_MUCH = False

EQUIPED_CHAR_ITEMS = {}

Rites = {}

Roll_history = []