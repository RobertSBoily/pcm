---Power & Magic Item Card Maker---

By Robert Boily

These scripts read the following two inputs:

1) A 4th Edition Dungeons and Dragons character file (.dnd4e) created by CBLoader. This is an XML file, typically ~1000 lines long.

2) The database of rules elements used by CBLoader - typically called 'combined.dnd40'. This is also an XML file, typically ~600 000 lines long.

The 'pcm_interfaceX' series of scripts creates a database with cards for the character's powers, while the 'icmX' series of scripts does the same for the character's magic items. Both scripts should be considered to be at version '0.X', with X being the number in the script.

In both cases, the output is a .mse-set file for being read by Magic Set Editor, and used with Ander00's power card template (originally posted and available at http://www.enworld.org/forum/showthread.php?220953-Making-your-own-power-cards/page57&p=4274554&viewfull=1#post4274554 ). This .mse-set file is simply a .zip file containing a file called 'set' (no file extension), which in turn is a .txt file with the information for the cards.
