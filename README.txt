---Power & Magic Item Card Maker---

By Robert Boily

These scripts interact with a few uncommon, and very niche programs, and so their purpose warrants some explanation.

This script was created to assist with running a Dungeons and Dragons: 4th Edition tabletop game. In this game, multiple people each play their own character, and each character has a multitude of powers and magic items. For convenience at the table, my group has been making cards for these powers and magic items - a card 63x88 mm in size, that contains the full rules text for one power or one magic item. Having such cards is essential for enjoying the game.

Before I made this script, we would tediously, manually type in all that rules text to an application called Magic Set Editor, which is an application for creating custom cards for a variety of games. Magic Set Editor stores its card databases in files with the extension '.mse-set'. These are actually .zip files; extracting them yields a single file, called 'set' (no file extension), which is in fact a .txt file, and contains all the information for the card, in a format custom-created for Magic Set Editor. 

We create our characters using CBLoader, an open-source extension of a Character Builder made by Wizards of the Coast, the company behind Dungeons and Dragons. CBLoader allows us to add our own custom content to the game, build characters easily, and share them electronically, all without flipping through several books.

CBLoader takes the original XML file from the Wizards of the Coast Character Builder, and combines it with several other XML files, called .part files, to create one combined database with all the rules elements in it - a file called 'combined.dnd40'. This is a 600 000 line XML file.

When used to create a character, CBLoader stores the choices you've made in another XML file, with the extension .dnd4e. Depending on the complexity of your character, it will typically be up to a few thousand lines long.

This script, in short, reads those two files - 'combined.dnd40' and '(MyCharacterName).dnd4e' - and produces a Magic Set Editor database with the extension .mse-set. The 'pcm_interfaceX' series of scripts creates a database with cards for the character's powers, while the 'icmX' series of scripts does the same for the character's magic items. Both scripts should be considered to be at version '0.X', with X being the number in the script.