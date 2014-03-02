SqlServer for SublimeText2
=====================================



Features
--------
    * Run sql commands on MS Sql Server directly from SublimeText2
    * Save commonly used server credentials and switch between them
    * Uh, not much else




Documentation
=============

In any sql window, hit F5 or Ctrl+Shift+B to execute the selected sql code. 
If you haven't selected any, it will execute the full contents of the view.
Output is shown in the output panel below.
You will be prompted to enter your DB credentials if you haven't saved any. 
Enter a valid sql server connection string.
It needs to have:
    * user id
    * pwd
    * data source
    * initial catalog

You can change the data source, by choosing the 'Set Sql Server Connection String' command from the Command Palette.
You can delete data sources by choosing 'Delete Sql Server Connection String' from the Command Palette.
Note: Internally, passwords are stored in plain text so you better be using this only for your dev environment.



#### Keybindings

* Evaluate selected sql:
 * <kbd>ctrl+shift+,</kbd>, <kbd>B</kbd>
 * <kbd>F5</kbd>




Compatibility
================

Requires osql.exe to be in your execution path.

