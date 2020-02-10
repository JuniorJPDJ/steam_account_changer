# Steam account changer

## How to use

First, You need to add your accounts to `acc.json` file in main directory. It's currently not automated :confused:  
Example file is provided, you just need to copy it and modify accounts username and passwords.  
Then If you want changer to show your stats and account info - run `./stats_loader.py`.  
It will ask you for your Guard codes if needed.  

Always when you want to update accounts data - run `./stats_loader.py` again.

To show your account data run `./changer.py` without parameters.
Example:
```
$ ./changer.py 
  SteamID3: [U:1:<steamid1>]
  | Login: <username1>                              | Name: <nickname1>
  | CS:GO:
    | Profile: Linked to <username2>                | Launch options: "-high -novid"
    | Rank: Not Ranked                              | Wins: 12
    | Level: 7                                      | Last MM: 2019-12-14 23:24
  | VAC bans: 0                                   
  SteamID3: [U:1:<steamid2>]
  | Login: <username2>                              | Name: <nickname2>
  | CS:GO:
    | Profile: Independent                          | Launch options: "-high -novid"
    | Rank: Not Ranked                              | Wins: 10
    | Level: 8                                      | Last MM: 2019-12-13 20:27
  | VAC bans: 0                                   
  SteamID3: [U:1:<steamid3>]
  | Login: <username3>                              | Name: <nickname3>
  | CS:GO:
    | Profile: Linked to <username2>                | Launch options: "-high -novid"
    | Rank: Not Ranked                              | Wins: 14
    | Level: 6                                      | Last MM: 2019-12-14 04:32
  | VAC bans: 0                                   
```

Then you can login to one of your accounts using login.
Example:
```
$ ./changer.py -l <username3>
```
You don't need to exit steam, It will be exited automatically.
