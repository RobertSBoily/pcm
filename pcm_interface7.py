import datetime
import os
import tkinter
import tkinter._fix # Needed for cx_freeze?
from tkinter import filedialog # Needed for cx_freeze
import unidecode # Non-library, for use in rules_text to remove troublesome non-ASCII characters.
import xml.etree.ElementTree as etree
import zipfile


# For use in get_powers().
STANDARD_CARDS = ('Melee Basic Attack', 'Ranged Basic Attack', 'Bull Rush Attack', 'Grab Attack', 'Opportunity Attack')

MANDATORY_KEYS = ('Display', 'Power Usage', 'Keywords')

# For use in get_rules_text() for attack_type.
BOLDED_WORDS = ('Melee', 'Ranged', 'Close', 'Area', 'Personal')

# For use in get_icons() for attack_type.
CORRECT_FIRST_WORDS = ('Ranged', 'Area', 'Personal')

ACTION_ICON_DICT = {'Standard Action' : 's',
                    'Move Action' : 'o',
                    'Minor Action' : 'm',
                    'Immediate Interrupt' : 'i',
                    'Immediate Reaction' : 'i',
                    'Free Action' : 'f',
                    'No Action' : 'f', # Unusual starts here
                    'Opportunity Action' : 'i',
                    '' : ''}

RANGE_ICON_DICT  = {'Melee' : 'e',
                    'Ranged' : 'r',
                    'Melee or Ranged' : 'n',
                    'Close blast' : 'b',
                    'Close burst' : 'u',
                    'Area' : 'U',
                    'Personal' : 'p',
                    'touch' : 't',
                    '' : ''}

# For use in get_background().
BACKGROUND_DICT  = {'at-will' : 'Green',
                    'encounter' : 'Red',
                    'daily' : 'Black',
                    'encounter (special)' : 'Blue', # Unusual starts here
                    'daily (special)' : 'Blue',
                    '' : 'Blue'}

# For use in abbreviate() to shorten above-the-box entries on the card.
ABBR_DICT        = {'Strength' : 'Str',
                    'Constitution' : 'Con',
                    'Dexterity' : 'Dex',
                    'Intelligence' : 'Int',
                    'Wisdom' : 'Wis',
                    'Charisma' : 'Cha',
                    'Fortitude' : 'Fort',
                    'Reflex' : 'Ref',
                    'Will' : 'Will'}

# For use in main() for opening combined.dnd40
DEFAULT_CBLOADER_PATH = os.path.expanduser('~/AppData/Roaming/CBLoader/combined.dnd40')
# For use in main() for finding character files
DEFAULT_CHAR_PATH = os.path.expanduser('~/Documents/ddi/Saved Characters/')


def get_power_names(filename):
    # filename must be a string such as 'Warden.dnd4e' that is the name of the 
    # Character Builder file to be scraped. 

    tree = etree.parse(filename)
    root = tree.getroot()
    character = root.find('CharacterSheet')

    # Find powers for making cards
    power_stats = character.find('PowerStats')
    powers = list(power_stats)

    power_names = []
    for power in powers:
        if power.get('name') not in STANDARD_CARDS:
            power_names.append(power.get('name'))

    # power_names is now a list of strings.
    # Each string is the name of a power possessed by the character.
    # The list is complete (has all of the character's powers), except those
    # listed in STANDARD_CARDS.
    return power_names

                    
def get_icons(rules_element):
    action_type = get_specific(rules_element, 'Action Type').title()
    attack_type = get_specific(rules_element, 'Attack Type')

    action_icon = ACTION_ICON_DICT[action_type]

    range_key = attack_type.split()

    # Force range_key to have at least 2 entries to avoid IndexError.
    while len(range_key) < 2:
        range_key.append('')
        
    range_icon = '' # Uses blank string if none of the conditions below are true.

    if range_key == []: # Power has no Attack Type
        range_icon = RANGE_ICON_DICT['']

    elif range_key[0] in CORRECT_FIRST_WORDS: # The first word of Attack Type tells us what icon to use.
        range_icon = RANGE_ICON_DICT[range_key[0]]
        
    elif range_key[0] == 'Melee': # The first word of Attack Type is 'Melee', still 3 possibilities for icons.
        if range_key[1] == 'or':
            range_icon = RANGE_ICON_DICT['Melee or Ranged']
        elif range_key[1] == 'touch':
            range_icon = RANGE_ICON_DICT['touch']
        else:
            range_icon = RANGE_ICON_DICT['Melee']
            
    elif range_key[0] == 'Close': # The first word of Attack Type is 'Close', still 2 possibilties for icons.
        if range_key[1] == 'blast':
            range_icon = RANGE_ICON_DICT['Close blast']
        else:
            range_icon = RANGE_ICON_DICT['Close burst']    
    
    return action_icon, range_icon


def get_power_display(rules_element):
    display = 'default'
    # If the rules element has display text, set the display variable to it.
    for child in rules_element:
        if child.get('name') == 'Display' and child.text: 
            display = child.text.split()
            while len(display) > 3: # Warlock (Infernal) fix; would give 4 words.
                del display[1]
            break
        
    if display == 'default':
        display = ['', '', '']
        
    while len(display) < 3: # Fixes short ones, eg Warden Feature
        display.append('')

    return display


def get_flavor_text(rules_element):
    for child in rules_element:
        if child.tag == 'Flavor':
            return child.text.strip()
    return ''


def get_power_rules_text(rules_element):
    # Returns a list of strings.
    # Each string is a line of the rules text.
    # Tabs and newline formatting will be added later.
    
    rules_text = []
    
    ## First line:    
    # <b>Action Type</b>' + '\t' + Attack Type with complex bolding
    # Every power has either 0 or 1 Action Types.
    # One power has 2 Attack Types, the rest have 0 or 1. 
    action_type = get_specific(rules_element, 'Action Type')
    attack_type = get_specific(rules_element, 'Attack Type')

    # All words in action_type should be in Title Case
    action_type = action_type.title()

    # Add bolding to attack_type.
    for word in BOLDED_WORDS:
        attack_type = attack_type.replace(word, '<b>' + word + '</b>')

    first_line = '<b>%s</b>\t%s' % (action_type, attack_type)
    rules_text.append(first_line)

    ## Subsequent lines:
    # Include all lines **between** 'Attack Type' and '_Associated Feats' ?
    included = False
    
    for child in rules_element:
        if child.get('name') in ('_Associated Feats', 'Class'): # Stop including immediately
            included = False
            
        if included and child.text and not child.text.isspace():
            new_line = '<b>%s:</b> %s' % (child.get('name'), child.text)
            new_line = new_line.replace('\n', '\n\t\t') # Fix Level 21 formatting problem.
            new_line = unidecode.unidecode(new_line) # Removes troublesome non-ASCII characters.
            rules_text.append(new_line)
            
        if child.get('name') == 'Attack Type': # Start including with the next child.
            included = True
    
    return rules_text
        

def get_specific(rules_element, name):
    # Used for anything other than Display or Flavor
    # If the rules element has multiple children with the relevant name (rare), this function returns the first.
    specific = ''
    for child in rules_element:
        if child.get('name') == name and child.text:
            return child.text.strip()
    return ''


def get_background(rules_element):
    # Returns a string for the appropriate color of the card.
    power_usage = get_specific(rules_element, 'Power Usage').lower()
    try:
        return BACKGROUND_DICT[power_usage]
    except KeyError as inst:
        print('Unusual "Power Usage": %s. Please set card color in MSE.' % (inst.args[0]))


def abbreviate(text):
    # Pass it a string, it abbreviates common D&D terms and returns the result.
    for word in ABBR_DICT:
        text = text.replace(word, ABBR_DICT[word])
    return text


def write_preamble(output):
    output.write('mse version: 0.3.8\n')
    output.write('game: D&D\n')
    output.write('stylesheet: Ander\n')
    output.write('set info:\n')
    output.write('\tsymbol:\n')
    output.write('styling:\n')
    output.write('\tD&D-Ander:\n')
    output.write('\t\tborder font color: White\n')
    output.write('\t\tlook: default\n')
    output.write('\t\ttext size: normal\n')
    output.write('\t\tflavor text size: small\n')
    output.write('\t\tname size: normal\n')


def write_postamble(output):
    output.write('version control:\n')
    output.write('\ttype: none\n')
    output.write('apprentice code:')
    output.close()
    

def get_timestamp():
    current_time = datetime.datetime(2000, 1, 1).today()
    timestamp = str(current_time).split('.')[0] # Cuts off the microseconds.
    return timestamp
    

def test_all_min_1(root, rules_element_type, child_name):
    # Present only for testing purpose: checking the full 4E library.
    broken_xml = []
    for rules_element in root:
        if rules_element.get('type') == rules_element_type:
            has_specific = False
            for child in rules_element:
                if child.get('name') == child_name:
                    has_specific = True
                    continue
                    
            if not has_specific:
                print('Found a %s without a %s: %s' % (rules_element_type, child_name, rules_element.get('name')))
                broken_xml.append(rules_element)
    return broken_xml


def test_all_max_1(root, rules_element_type, child_name):
    # Present only for testing purpose: checking the full 4E library.
    broken_xml = []
    for rules_element in root:
        if rules_element.get('type') == rules_element_type:
            count = 0
            for child in rules_element:
                if child.get('name') == child_name:
                    count += 1
            if count > 1:
                print('Found a %s with more than one %s: %s' % (rules_element_type, child_name, rules_element.get('name')))
                broken_xml.append(rules_element)
    return broken_xml


def get_all_powers(database):
    # Pass it the string for the local filename of the CBLoader main database.
    # Exists only for testing compatibility.
    tree = etree.parse(database)
    root = tree.getroot()

    all_powers = []

    for child in root:
        if child.get('type') == 'Power':
            all_powers.append(child)

    return all_powers

            
def main():
    # Get the tree from combined.dnd40
    if os.path.exists('combined.dnd40'): # Check if combined.dnd40 is in the same folder as the executable.
        print("Using database found in this program's folder.")
        tree = etree.parse('combined.dnd40')
        
    elif os.path.exists(DEFAULT_CBLOADER_PATH): # Check if combined.dnd40 is in default location
        print("Using database found at %s" % (DEFAULT_CBLOADER_PATH))
        tree = etree.parse(DEFAULT_CBLOADER_PATH)
        
    else:
         print("Unable to find the CBLoader database. Please locate your combined.dnd40 file and copy it into this program's folder, then run this program again.")
         input("Press Enter to exit.")
        
    root = tree.getroot()

    # Eliminate blank dialog (tkinter's root window)
    blank_dialog = tkinter.Tk()
    blank_dialog.withdraw()
     
    # Get power names from the character file.
    character = tkinter.filedialog.askopenfilename(initialdir=DEFAULT_CHAR_PATH, title="Open your .dnd4e character file") # Get filename to open
    
    power_names = get_power_names(character)

    global power_xml    
    power_xml = []
    

    # Get the xml for the named powers.
    for power in power_names:
        for child in root: # Could maybe use a find function here, for speed. Save a few seconds.
            if child.get('name') == power and child.get('type') == 'Power':
                power_xml.append(child)
                break

    # power_xml is now a list, each item is the XML data for one power we want included

    output = open('set', 'w')

    # Write the preamble.
    write_preamble(output)


    # Write the cards.
    for rules_element in power_xml:
        # The following variables are set in the order that they will be used.
        timestamp               = get_timestamp()
        name                    = rules_element.get('name')
        
        print('Writing card: ' + name) # Progress reporting
        
        display                 = get_power_display(rules_element)
        power_usage             = get_specific(rules_element, 'Power Usage')
        keywords                = get_specific(rules_element, 'Keywords')
        rules_text              = get_power_rules_text(rules_element)
        flavor_text             = get_flavor_text(rules_element)
        action_icon, range_icon = get_icons(rules_element)
        attack                  = abbreviate(get_specific(rules_element, 'Attack')) # Doesn't work right for Rangers.
        # Get Primary attack, for those with both Primary and Secondary.
        if not attack:
            attack              = abbreviate(get_specific(rules_element, 'Primary Attack'))
        background              = get_background(rules_element)
        
        output.write('card:\n')
        output.write('\thas styling: true\n')
        output.write('\tstyling data:\n')
        output.write('\t\tborder font color: White\n')
        output.write('\tnotes: Created with Python\n')
        output.write('\ttime created: %s\n' % (timestamp))
        output.write('\ttime modified: %s\n' % (timestamp))
        output.write('\tname: %s\n' % (name))
        output.write('\timage:\n')
        output.write('\tsuper type: <word-list-type>%s</word-list-type>\n' % (display[0]))
        output.write('\tsub type: <word-list-class>%s</word-list-class>\n' % (display[1]))
        output.write('\tlevel: %s\n' % (display[2]))
        output.write('\tdescriptors: <word-list-frequency>%s</word-list-frequency><sep> <sym>$</sym> </sep>%s\n' % (power_usage, keywords))
        output.write('\tfrequency: <word-list-frequency>%s</word-list-frequency>\n' % (power_usage))
        output.write('\tflags: %s\n' % (keywords))
        output.write('\trule text:\n')
        # Write the rules text.
        for line in rules_text:
            output.write('\t\t')
            output.write(line)
            output.write('\n')
        # Rules text done.
        output.write('\tflavor text: <i-flavor>%s</i-flavor>\n' % (flavor_text))
        output.write('\taction icon: %s\n' % (action_icon))
        output.write('\trange icon: %s\n' % (range_icon))
        # Optional box labels. Never does the third box, have to check manually.
        if attack:
            output.write('\tattack: %s\n' % (attack))
            output.write('\tbox label5: %s\n' % ('Damage'))
        output.write('\tbackground: %s\n' % (background))
        
        
    # Write the postamble and close the document.
    write_postamble(output)

    # Create the .mse-set zip file. Leaves 'set' intact, but it will be overwritten the next time the program is run.
    save_name = tkinter.filedialog.asksaveasfilename(defaultextension='.mse-set', title='Save the Magic Set Editor file')
    mse_file = zipfile.ZipFile(save_name, 'w', zipfile.ZIP_STORED, False)
    mse_file.write('set')
    mse_file.close()

    print('Done.')
    input('Press Enter to exit.')


if __name__ == '__main__':
    main()
