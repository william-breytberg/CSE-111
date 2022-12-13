import sqlite3
from sqlite3 import Error
import pokepy
import numpy as np

def openConnection(_dbFile):
    print("++++++++++++++++++++++++++++++++++")
    print("Open database: ", _dbFile)
    conn = None
    try:
        conn = sqlite3.connect(_dbFile)
        print("success")
    except Error as e:
        print(e)
    print("++++++++++++++++++++++++++++++++++")
    return conn

def closeConnection(_conn, _dbFile):
    print("++++++++++++++++++++++++++++++++++")
    print("Close database: ", _dbFile)
    try:
        _conn.close()
        print("success")
    except Error as e:
        print(e)
    print("++++++++++++++++++++++++++++++++++")


def createTable(_conn):
    print("++++++++++++++++++++++++++++++++++")
    print("Create table")
    try:
        _conn.execute("""CREATE TABLE pokemon (
            dexNum smallint NOT NULL,
            species varchar(16) PRIMARY KEY,
            category varchar(64) NOT NULL,
            type1 varchar(16) NOT NULL,
            type2 varchar(16),
            ability1 varchar(32) NOT NULL,
            ability2 varchar(32),
            ability3 varchar(32),
            femRatio float(24),
            eggGroup1 varchar(32) NOT NULL,
            eggGroup2 varchar(32),
            bodyShape varchar(64) NOT NULL,
            weight float(24),
            height float(24),
            movelist text NOT NULL
        )""")
        _conn.execute("""CREATE TABLE move (
            name varchar(32) PRIMARY KEY,
            type varchar(16) NOT NULL,
            category varchar(8) NOT NULL,
            power tinyint,
            accuracy tinyint,
            pp tinyint
        )""")
        _conn.execute("""CREATE TABLE type (
            name varchar(32) PRIMARY KEY,
            weakness text NOT NULL,
            resistance text,
            immunity text
        )""")
        _conn.execute("""CREATE TABLE baseStats (
            species varchar(16) PRIMARY KEY,
            hp smallint NOT NULL,
            attack smallint NOT NULL,
            defense smallint NOT NULL,
            spatk smallint NOT NULL,
            spdef smallint NOT NULL,
            speed smallint NOT NULL
        )""")
        _conn.execute("""CREATE TABLE effValues (
            species varchar(16) PRIMARY KEY,
            hp smallint NOT NULL,
            attack smallint NOT NULL,
            defense smallint NOT NULL,
            spatk smallint NOT NULL,
            spdef smallint NOT NULL,
            speed smallint NOT NULL
        )""")
        print("success")
    except Error as e:
        print(e)
    print("++++++++++++++++++++++++++++++++++")

    
def populateTable(_conn):
    print("++++++++++++++++++++++++++++++++++")
    print("Populate table")
    client = pokepy.V2Client()
    cur = _conn.cursor()
    try:
        allmoves = []
        for n in range(1,722):
            mon = client.get_pokemon(n)
            spec = mon.name
            species = client.get_pokemon_species(n)
            g = species.genera[7].genus
            t = [None,None]
            i = 0
            for typ in mon.types:
                t[i] = typ.type.name
                i+=1
            a = [None,None,None]
            i = 0
            for abi in mon.abilities:
                a[i] = abi.ability.name
                i+=1
            femRatio = species.gender_rate
            e = [None,None]
            i = 0
            for egg in species.egg_groups:
                e[i] = egg.name
                i+=1
            bodyShape = species.shape.name
            weight = mon.weight
            height = mon.height
            movelist = ","
            for m in mon.moves:
                name = m.move.name
                movelist += name + ","
                if name not in allmoves:
                    allmoves.append(name)
                    mo = client.get_move(name)
                    typeM = mo.type.name
                    category = mo.damage_class.name
                    power = mo.power
                    accuracy = mo.accuracy
                    pp = mo.pp
                    cur.execute("INSERT INTO move VALUES(?,?,?,?,?,?)",[name,typeM,category,power,accuracy,pp])
                    print(["     MOVE:",name,typeM,category,power,accuracy,pp])
            cur.execute("INSERT INTO pokemon VALUES(?,   ?,?,   ?,   ?,   ?,   ?,   ?,       ?,   ?,   ?,        ?,     ?,     ?,?)",
                                                   [n,spec,g,t[0],t[1],a[0],a[1],a[2],femRatio,e[0],e[1],bodyShape,weight,height,movelist])
            ev = [0,0,0,0,0,0]
            bs = [0,0,0,0,0,0]
            for stat in range(5):
                ev[stat] = mon.stats[stat].effort
                bs[stat] = mon.stats[stat].base_stat
            cur.execute("INSERT INTO baseStats VALUES (?,?,?,?,?,?,?)",[spec,bs[0],bs[1],bs[2],bs[3],bs[4],bs[5]])
            cur.execute("INSERT INTO effValues VALUES (?,?,?,?,?,?,?)",[spec,ev[0],ev[1],ev[2],ev[3],ev[4],ev[5]])
            print(["POKE:",n,spec,g,t[0],t[1],a[0],a[1],a[2],femRatio,e[0],e[1],bodyShape,weight,height,movelist])
            print([" BASE:",spec,bs[0],bs[1],bs[2],bs[3],bs[4],bs[5]])
            print(["  EFVS:",spec,ev[0],ev[1],ev[2],ev[3],ev[4],ev[5]])
        typeList = [
        #   type        weaknesses                            resistances                                                     immunities
            ("bug",     ",fire,flying,rock,",                 ",fighting,grass,ground,",                                      None),
            ("fire",    ",ground,water,rock,",                ",bug,grass,fire,fairy,steel,ice,",                             None),
            ("water",   ",electric,grass,",                   ",fire,water,steel,ice,",                                       None),
            ("grass",   ",bug,fire,flying,ice,poison,",       ",electric,grass,ground,water,",                                None),
            ("steel",   ",fighting,fire,ground,",             ",bug,grass,flying,fairy,steel,ice,normal,psychic,rock,dragon,",",poison,"),
            ("poison",  ",ground,psychic,",                   ",fighting,poison,bug,grass,fairy,",                            None),
            ("ground",  ",grass,ice,water,",                  ",poison,rock,",                                                ",electric,"),
            ("rock",    ",fighting,grass,ground,steel,water,",",fire,flying,normal,poison,",                                  None),
            ("fighting",",fairy,flying,psychic,",             ",bug,dark,rock,",                                              None),
            ("normal",  ",fighting,",                         None,                                                           ",ghost,"),
            ("ghost",   ",dark,ghost,",                       ",bug,poison,",                                                 ",normal,fighting,"),
            ("dark",    ",bug,fairy,fighting,",               ",dark,ghost,",                                                 ",psychic,"),
            ("ice",     ",fire,rock,fighting,steel,",         ",ice,",                                                        None),
            ("electric",",ground,",                           ",electric,flying,steel,",                                      None),
            ("dragon",  ",dragon,ice,fairy,",                 ",electric,fire,grass,water,",                                  None),
            ("fairy",   ",poison,steel,",                     ",bug,dark,fighting,",                                          ",dragon,"),
            ("psychic", ",bug,dark,ghost,",                   ",fighting,psychic,",                                           None)
        ]
        cur.executemany("INSERT INTO type VALUES(?,?,?,?)",typeList)    
        print("success")
    except Error as e:
        print(e)
    print("++++++++++++++++++++++++++++++++++")

def dropTable(_conn):
    print("++++++++++++++++++++++++++++++++++")
    print("Drop tables")
    try:
        _conn.execute("DROP TABLE pokemon")
        _conn.execute("DROP TABLE move")
        _conn.execute("DROP TABLE type")
        _conn.execute("DROP TABLE baseStats")
        _conn.execute("DROP TABLE effValues")
        print("success")
    except Error as e:
        print(e)
    print("++++++++++++++++++++++++++++++++++")


def main():
    database = r"tpch.sqlite"
    conn = openConnection(database)
    with conn:
        # dropTable(conn)
        # createTable(conn)
        # populateTable(conn)
        q1 = input("Would you like to search for a \"move\" or a \"Pokemon\"?\n(Use only complete, exact resposes.)\n")
        qcon = True
        qfin = False
        sqlQ = "WHERE "
        pE = False
        pB = False
        if q1 == "move":
            while qcon:
                q2 = input("How would you like to search through moves?\n•name\n•type\n•category\n•power\n•accuracy\n•pp\n")
                if q2 == "name":
                    q3 = input("Please input a string of characters to search for within the move's name, all lower-case.\n(SQL formatting is accepted.)\n")
                    sqlQ += "move.name LIKE \"%" + q3 + "%\" "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                elif q2 == "type":
                    q3 = input("Please specify the type of the moves to search for, all lower-case.\n(SQL formatting is accepted.)\n")
                    sqlQ += "move.type LIKE \"" + q3 + "\" "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                elif q2 == "category":
                    q3 = input("Please specify whether the move is \"physical\",\"special\", or \"status\".\n")
                    sqlQ += "move.category LIKE \"" + q3 + "\" "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                elif q2 == "power":
                    q3 = input("Please specify a numerical value.\n")
                    qN = input("Please specify whether you want the moves filtered to have a (g)reater, (l)esser, or (e)qual power.\n")
                    if qN ==  "g":
                        sqlQ += "move.power > "
                    elif qN ==  "l":
                        sqlQ += "move.power < "
                    else:
                        sqlQ += "move.power = "
                    sqlQ += str(q3) + " "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                elif q2 == "accuracy":
                    q3 = input("Please specify a numerical value.\n")
                    qN = input("Please specify whether you want the moves filtered to have a (g)reater, (l)esser, or (e)qual accuracy.\n")
                    if qN ==  "g":
                        sqlQ += "move.accuracy > "
                    elif qN ==  "l":
                        sqlQ += "move.accuracy < "
                    else:
                        sqlQ += "move.accuracy = "
                    sqlQ += str(q3) + " "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                elif q2 == "pp":
                    q3 = input("Please specify a numerical value.\n")
                    qN = input("Please specify whether you want the moves filtered to have a (g)reater, (l)esser, or (e)qual PP.\n")
                    if qN ==  "g":
                        sqlQ += "move.pp > "
                    elif qN ==  "l":
                        sqlQ += "move.pp < "
                    else:
                        sqlQ += "move.pp = "
                    sqlQ += str(q3) + " "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                else:
                    print("Invalid response received. Please reboot.")
                    qcon = False
            if qfin:
                sqlQ = "SELECT name FROM move " + sqlQ + ";"
                cur = conn.cursor()
                try:
                    cur.execute(sqlQ)
                    table = cur.fetchall()
                    for elem in table:
                        print(elem[0])
                except Error as e:
                    print(e)
        elif q1 == "Pokemon":
            while qcon:
                q2 = input("How would you like to search through Pokemon?\n•name\n•type\n•category\n•ability\n•base stats\n•given EVs\n•egg group\n•move\n")
                if q2 == "name":
                    q3 = input("Please input a string of characters to search for within the Pokemon's name, all lower-case.\n(SQL formatting is accepted.)\n")
                    sqlQ += "pokemon.species LIKE \"%" + q3 + "%\" "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                if q2 == "category":
                    q3 = input("Please input a string of characters to search for within the Pokemon's category.\n(SQL formatting is accepted.)\n")
                    sqlQ += "pokemon.category LIKE \"%" + q3 + "%\" "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                if q2 == "move":
                    q3 = input("Please input the exact name of a move to search for within the Pokemon's movepool.\n(SQL formatting is accepted.)\n")
                    sqlQ += "pokemon.movelist LIKE \"%," + q3 + ",%\" "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                elif q2 == "type":
                    q3 = input("Please specify the type of the Pokemon to search for, all lower-case.\n(SQL formatting is accepted.)\n")
                    sqlQ += "(pokemon.type1 LIKE \"" + q3 + "\" OR pokemon.type2 LIKE \"" + q3 + "\") "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                elif q2 == "egg group":
                    q3 = input("Please specify the egg group of the Pokemon to search for, all lower-case.\n(SQL formatting is accepted.)\n")
                    sqlQ += "(pokemon.eggGroup1 LIKE \"" + q3 + "\" OR pokemon.eggGroup2 LIKE \"" + q3 + "\") "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                elif q2 == "ability":
                    q3 = input("Please specify the exact name of the ability of the Pokemon to search for, all lower-case.\n(SQL formatting is accepted.)\n")
                    sqlQ += "(pokemon.ability1 LIKE \"" + q3 + "\" OR pokemon.ability2 LIKE \"" + q3 + "\" OR pokemon.ability3 LIKE \"" + q3 + "\") "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                elif q2 == "base stats":
                    pB = True
                    q3 = input("Please specify a numerical value.\n")
                    qN = input("Please specify whether you want the Pokemon filtered to have a (g)reater, (l)esser, or (e)qual base stat.\n")
                    qStat = input("Please specify which base stat you wish to filter along.\n•hp\n•attack\n•defense\n•spatk\n•spdef\n•speed\n")
                    if qN ==  "g":
                        sqlQ += "baseStats." + qStat + " > "
                    elif qN ==  "l":
                        sqlQ += "baseStats." + qStat + " < "
                    else:
                        sqlQ += "baseStats." + qStat + " = "
                    sqlQ += str(q3) + " "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                elif q2 == "given EVs":
                    pE = True
                    q3 = input("Please specify a numerical value.\n")
                    qN = input("Please specify whether you want the Pokemon filtered to have a (g)reater, (l)esser, or (e)qual effort value yield.\n")
                    qStat = input("Please specify which effort value you wish to filter along.\n•hp\n•attack\n•defense\n•spatk\n•spdef\n•speed\n")
                    if qN ==  "g":
                        sqlQ += "effValues." + qStat + " > "
                    elif qN ==  "l":
                        sqlQ += "effValues." + qStat + " < "
                    else:
                        sqlQ += "effValues." + qStat + " = "
                    sqlQ += str(q3) + " "
                    q4 = input("Would you like to include other parameters? (Y/N)\n")
                    if q4 == "N":
                        qcon = False
                        qfin = True
                    elif q4 == "Y":
                        sqlQ += "AND "
                    else:
                        print("Invalid response received. Please reboot.")
                        qcon = False
                else:
                    print("Invalid response received. Please reboot.")
                    qcon = False
            if qfin:
                if pE:
                    sqlQ = ",effValues " + sqlQ + "AND effValues.species = pokemon.species "
                if pB:
                    sqlQ = ",baseStats " + sqlQ + "AND baseStats.species = pokemon.species "
                sqlQ = "SELECT pokemon.dexNum, pokemon.species FROM pokemon " + sqlQ + ";"
                cur = conn.cursor()
                try:
                    cur.execute(sqlQ)
                    table = cur.fetchall()
                    for elem in table:
                        print(str(elem[0]) + " | " + elem[1])
                except Error as e:
                    print(e)
        else:
            print("Invalid response received. Please reboot.")
    closeConnection(conn, database)
if __name__ == '__main__':
    main()
