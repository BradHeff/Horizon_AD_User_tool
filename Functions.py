import base64
import sys
import configparser_crypt as cCrypt
import OpenSSL
from os import mkdir, path, removedirs, system, name  # noqa
import json

if name == "nt":
    import win32security


from pathlib import Path
from ttkbootstrap import DISABLED, NORMAL
from ttkbootstrap.toast import ToastNotification

# from flask import json
from ldap3 import Connection, Server, MODIFY_REPLACE, SAFE_SYNC, SUBTREE, Tls
from ldap3.extend.microsoft.removeMembersFromGroups import (
    ad_remove_members_from_groups as removeUsersInGroups,
)

DEBUG = True
Version = "v2.0.9.8"
key = b'\xc2\x04_\x8e\xd2\xed7H\x0e\x9b,m\xc1pE\xe9\xdd$\xa9\xdb\x83\x06\xe5l#d\x13"o\x00tc'
settings_file = "Settings.dat"
UAC = 32 + 65536
ICT_Admins = {
    "IT": ["bheffernan", "brad.heff.desktop"],
    "Management": ["djohnson", "dan.desktop"],
}

tls_configuration = Tls(
    validate=OpenSSL.SSL.VERIFY_NONE, version=OpenSSL.SSL.TLSv1_1_METHOD
)
if not DEBUG:
    exe_dir = str(path.dirname(sys.executable))
else:
    exe_dir = str(Path(__file__).parents[0])

if name == "nt":
    settings_dir = "".join([exe_dir, "\\Settings\\"])
    temp_dir = "".join([exe_dir, "\\Tmp\\"])
else:
    settings_dir = "".join([exe_dir, "/Settings/"])
    temp_dir = "".join([exe_dir, "/Tmp/"])


def Toast(title, message, types="happy"):
    happy = "😀"
    sad = "😟"
    angry = "🤬"
    icon = ""
    if "er" in types:
        icon = angry
    elif "war" in types:
        icon = sad
    else:
        icon = happy
    toast = ToastNotification(
        title=title,
        message=message,
        icon=icon,
        duration=10000,
    )
    toast.show_toast()


def clear_console():
    system("cls")


def Switch(string, lists):
    if string.lower() in lists:
        return True
    else:
        return False


def checkSettings(self, company):
    if base64.b64decode(company).decode("UTF-8").__len__() >= 2:
        return True
    else:
        return False


def ldap_connection(self):
    server = Server(
        base64.b64decode(self.server).decode("UTF-8").strip(),
        use_ssl=True,
        tls=tls_configuration,
    )

    return Connection(
        server,
        base64.b64decode(self.username).decode("UTF-8").strip(),
        base64.b64decode(self.password).decode("UTF-8").strip(),
        client_strategy=SAFE_SYNC,
        auto_bind=True,
    )


def ldap_login(self, username, password):
    server = Server(
        base64.b64decode(self.server).decode("UTF-8").strip(),
        use_ssl=True,
        tls=tls_configuration,
    )
    return Connection(
        server,
        "".join([self.company, "\\", username.strip()]),
        password.strip(),
        client_strategy=SAFE_SYNC,
        auto_bind=True,
    )


def get_operation_result(connection, operation_result):
    if not connection.strategy.sync:
        _, result = connection.get_response(operation_result)
    else:
        result = connection.result

    return result


def saveConfig(self):
    parser = cCrypt.ConfigParserCrypt()
    parser["config"] = {}
    if "Select" not in self.options.get():
        parser["config"]["autoload"] = str(self.load.get())
        parser["config"]["company"] = self.options.get()
        parser["config"]["tab"] = str(self.tabControl.index(self.tabControl.select()))

        if not self.var.get() == "1":
            parser["newuser"] = {}
            data = getnewuser(self)
            parser["newuser"]["domain"] = data["domain"]
            parser["newuser"]["campus"] = data["campus"]
            parser["newuser"]["password"] = data["password"]
            parser["newuser"]["format"] = data["format"]
            parser["newuser"]["pos"] = data["pos"]
            parser["newuser"]["hdrive"] = data["hdrive"]
            parser["newuser"]["hpath"] = data["hpath"]
            parser["newuser"]["desc"] = data["desc"]
            parser["newuser"]["title"] = data["title"]

    with open(settings_dir + "Config.ini", "w") as w:
        parser.write(w)


def loadConfig(self, check=False):
    parser = cCrypt.ConfigParserCrypt()
    parser.read(settings_dir + "Config.ini")
    if parser.has_section("config"):
        if parser.has_option("config", "autoload"):
            self.load.set(eval(parser.get("config", "autoload")))
    if eval(parser.get("config", "autoload")) or check is True:
        if parser.has_option("config", "tab"):
            self.tabControl.select(int(parser.get("config", "tab")))
        if parser.has_section("newuser"):
            self.campH.set(parser.get("newuser", "campus"))
            self.var.set(parser.get("newuser", "pos"))
            self.posSelect("H")
            self.samFormat.set(parser.get("newuser", "format"))
            self.primary_domain.set(parser.get("newuser", "domain"))
            self.hdrive.set(parser.get("newuser", "hdrive"))
            self.paths.set(parser.get("newuser", "hpath"))
            self.desc.delete(0, "end")
            self.dpass.delete(0, "end")
            self.jobTitleEnt.delete(0, "end")
            self.dpass.insert(0, parser.get("newuser", "password"))
            self.desc.insert(0, parser.get("newuser", "desc"))
            self.jobTitleEnt.insert(0, parser.get("newuser", "title"))
            self.loaded = True
            # self.comboLoad()


def getServer(self, section):  # noqa
    parser = cCrypt.ConfigParserCrypt()
    parser.aes_key = key
    parser.read_encrypted(settings_dir + settings_file)
    if parser.has_section(section):
        if parser.has_option(section, "server"):
            return parser.get(section, "server")
            # print(base64.b64decode(self.server).decode("UTF-8"))
            if not base64.b64decode(self.server).decode("UTF-8").__len__() <= 3:
                return False
            else:
                return False


def getSettings(self):
    parser = cCrypt.ConfigParserCrypt()
    parser.aes_key = key
    parser.read_encrypted(settings_dir + settings_file)
    if parser.has_section("Settings"):
        return parser.get("Settings", "company")


def getConfig(self, section):  # noqa
    parser = cCrypt.ConfigParserCrypt()
    parser.aes_key = key
    parser.read_encrypted(settings_dir + settings_file)

    if parser.has_section(section):
        # ===================SERVER================================
        if parser.has_option(section, "server"):
            self.server = parser.get(section, "server")
            # print(base64.b64decode(self.server).decode("UTF-8"))
            if not base64.b64decode(self.server).decode("UTF-8").__len__() <= 3:
                self.compFail = False
                self.servs = True
            else:
                self.compFail = True
                self.servs = False
                return
        # ===================SERVER USERNAME================================
        if parser.has_option(section, "server_user"):
            self.username = parser.get(section, "server_user")
            # print(base64.b64decode(self.username).decode("UTF-8"))
            if not base64.b64decode(self.username).decode("UTF-8").__len__() <= 3:
                self.compFail = False
                self.servs = True
            else:
                self.compFail = True
                self.servs = False
                return
        # ===================SERVER PASSWORD================================
        if parser.has_option(section, "server_pass"):
            self.password = parser.get(section, "server_pass")
            # print(base64.b64decode(self.password).decode("UTF-8"))
            if not base64.b64decode(self.password).decode("UTF-8").__len__() <= 3:
                self.compFail = False
                self.servs = True
            else:
                self.compFail = True
                self.servs = False
                return
        # ===================USEROU================================
        if parser.has_option(section, "userou"):
            self.ou = parser.get(section, "userou")
            if not base64.b64decode(self.ou).decode("UTF-8").__len__() <= 3:
                self.compFail = False
                self.servs = True
            else:
                self.compFail = True
                self.servs = False
                return
        # ===================DOMAIN NAME================================
        if parser.has_option(section, "domainname"):
            self.domainName = parser.get(section, "domainname")
            if base64.b64decode(self.domainName).decode("UTF-8").__len__() <= 3:
                self.state = True

        # ===================POSITIONS================================
        if parser.has_option(section, "positions"):
            JSON1 = base64.b64decode(parser.get(section, "positions")).decode("UTF-8")
            JSON1 = JSON1.replace("'", '"')
            self.positions = json.loads(JSON1)
            if self.positions.__len__() <= 3:
                self.state = True

        # ===================GROUPS================================
        if parser.has_option(section, "groups"):
            JSON2 = base64.b64decode(parser.get(section, "groups")).decode("UTF-8")
            JSON2 = JSON2.replace("'", '"')
            self.groupPos = json.loads(JSON2)
            if self.groupPos.__len__() <= 3:
                self.state = True

        # ===================POSITIONS OU================================
        if parser.has_option(section, "positionsou"):
            JSON3 = base64.b64decode(parser.get(section, "positionsou")).decode("UTF-8")
            JSON3 = JSON3.replace("'", '"')
            self.positionsOU = json.loads(JSON3)
            if self.positionsOU.__len__() <= 3:
                self.state = True

        # ===================EXPIRED OU================================
        if parser.has_option(section, "expiredous"):
            JSON4 = base64.b64decode(parser.get(section, "expiredous")).decode("UTF-8")
            JSON4 = JSON4.replace("'", '"')
            self.expiredOUs = json.loads(JSON4)
            if self.expiredOUs.__len__() <= 3:
                self.state = True

        # ===================GROUP OU================================
        if parser.has_option(section, "groupsou"):
            self.groupOU = parser.get(section, "groupsou")
            # print(base64.b64decode(self.groupOU).decode("UTF-8"))
            if base64.b64decode(self.groupOU).decode("UTF-8").__len__() <= 3:
                self.state = True

        # ===================DOMAINS================================
        if parser.has_option(section, "domains"):
            JSON5 = base64.b64decode(parser.get(section, "domains")).decode("UTF-8")
            JSON5 = JSON5.replace("'", '"')
            self.domains = json.loads(JSON5)
            if self.domains.__len__() <= 3:
                self.state = True

        # ===================HOME DIRECTORIES================================
        if parser.has_option(section, "homepaths"):
            self.homePaths = parser.get(section, "homepaths")
            if (
                base64.b64decode(self.homePaths).decode("UTF-8").split(",").__len__()
                <= 3
            ):
                self.state = True

        # ===================TITLES================================
        if parser.has_option(section, "title"):
            JSON6 = base64.b64decode(parser.get(section, "title")).decode("UTF-8")
            JSON6 = JSON6.replace("'", '"')
            self.jobTitle = json.loads(JSON6)
            if self.jobTitle.__len__() <= 3:
                self.state = True

        # ===================HOME DIRECTORIES================================
        if parser.has_option(section, "campus"):
            self.campus = parser.get(section, "campus")
            # print(base64.b64decode(self.campus).decode("UTF-8").split(","))
            if (
                not base64.b64decode(self.campus).decode("UTF-8").split(",").__len__()
                > 0
            ):
                self.state = True
        else:
            self.compFail = True
    else:
        self.compFail = True

    if not self.compFail:
        self.state = False
        widgetStatus(self, NORMAL)


def getnewuser(self):
    data = dict()
    data["format"] = self.samFormat.get()
    data["pos"] = self.var.get()
    data["campus"] = str(self.campH.get())
    data["domain"] = self.primary_domain.get()
    data["password"] = self.dpass.get()
    data["hdrive"] = self.hdrive.get()
    data["hpath"] = self.paths.get()
    data["desc"] = self.desc.get()
    data["title"] = self.jobTitleEnt.get()
    return data


def widgetStatus(self, status):
    if status == NORMAL:
        self.combobox["state"] = "readonly"
    else:
        self.combobox["state"] = DISABLED

    self.btn_unlockAll["state"] = status
    self.btn_search["state"] = status
    self.btn_userUnlock["state"] = status
    self.btn_reset["state"] = status
    # self.move_btn["state"] = status
    # self.addGroup["state"] = status


def widgetStatusFailed(self, state):
    if state:
        self.btn_unlockAll["state"] = DISABLED
        self.btn_search["state"] = DISABLED
        self.btn_userUnlock["state"] = DISABLED
        self.btn_reset["state"] = DISABLED
        # self.move_btn["state"] = DISABLED
        # self.addGroup["state"] = DISABLED
    else:
        self.btn_unlockAll["state"] = NORMAL
        self.btn_search["state"] = NORMAL
        self.btn_userUnlock["state"] = NORMAL
        self.btn_reset["state"] = NORMAL
        # self.addGroup["state"] = NORMAL


def resetPassword(self, ou, newpass):
    selected_item = self.tree.selection()[0]
    try:
        with ldap_connection(self) as c:
            c.extend.microsoft.modify_password(
                user=ou, new_password=newpass, old_password=None
            )
            result = c.modify(
                dn=ou,
                changes={"lockoutTime": "0"},
            )
            if not result:
                msg = "ERROR: '{0}'".format(
                    c.result.get("description"),
                )
                raise Exception(msg)

        self.tree.delete(selected_item)
        self.selItem = []
        widgetStatus(self, NORMAL)
        # self.messageBox("SUCCESS!!", "Password set and user unlocked!")
        Toast("SUCCESS!!", "Password set and user unlocked!", "happy")
    except:  # noqa
        self.selItem = []
        widgetStatus(self, NORMAL)
        Toast("ERROR!!", "An error has occured!", "angry")
        # self.messageBox("ERROR!!", "An error has occured!")


def unlockUser(self, ou, all=0):
    self.status["text"] = "".join(["Unlocking ", ou.split(",")[0].replace("CN=", "")])
    with ldap_connection(self) as c:
        result = c.modify(
            dn=ou,
            changes={"lockoutTime": (MODIFY_REPLACE, ["0"])},
        )
        if not result:
            msg = "ERROR: '{0}'".format(
                c.result.get("description"),
            )
            raise Exception(msg)

    if all == 0:
        widgetStatus(self, NORMAL)


def unlockAll(self, locked):
    count = 0
    props = 1
    for x in locked:
        count += 1
        if count == self.all:
            props = 0
        self.status["text"] = "".join(["Unlocking ", locked[x]["name"]])
        self.progress["value"] = count
        unlockUser(self, locked[x]["ou"], all=props)
    self.tree.delete(*self.tree.get_children())
    widgetStatus(self, NORMAL)
    self.status["text"] = "Idle..."
    Toast("SUCCESS!!", "Unlock Complete!", "happy")
    # self.messageBox("SUCCESS!!", "Unlock Complete!")
    self.progress["value"] = 0


def listLocked(self):
    users = {}
    with ldap_connection(self) as c:
        status, result, response, _ = c.search(
            search_base=base64.b64decode(self.ou).decode("UTF-8"),
            search_filter="(&(objectClass=user)(objectCategory=person)(lockoutTime>=1))",
            search_scope=SUBTREE,
            attributes=[
                "displayName",
                "lockoutTime",
                "distinguishedName",
                "sAMAccountName",
            ],
            get_operational_attributes=True,
        )

        for x in response:
            res = x["attributes"]
            # print(res["displayName"])
            users[res["sAMAccountName"]] = {
                "name": res["displayName"],
                "ou": res["distinguishedName"],
            }
    # print(users)
    return users


def update_user(self, data):
    # try:
    self.status["text"] = "".join(["Updating ", data["first"], " ", data["last"]])
    with ldap_connection(self) as c:
        self.progress["value"] = 60

        if data["proxy"] is None:
            proxy = "".join(["smtp:", data["login"], "@", self.domains["Secondary"]])
        else:
            proxy = "".join(["smtp:", data["login"], "@", data["proxy"]])

        attributes = {
            "givenName": (MODIFY_REPLACE, [data["first"]]),
            "sAMAccountName": (MODIFY_REPLACE, [data["login"]]),
            "sn": (MODIFY_REPLACE, [data["last"]]),
            "DisplayName": (
                MODIFY_REPLACE,
                ["".join([data["first"], " ", data["last"]])],
            ),
            "title": (MODIFY_REPLACE, [data["title"]]),
            "description": (MODIFY_REPLACE, [data["description"]]),
            "userPrincipalName": (
                MODIFY_REPLACE,
                ["".join([data["login"], "@", data["domain"]])],
            ),
            "mail": (
                MODIFY_REPLACE,
                ["".join([data["login"], "@", data["domain"]])],
            ),
            "proxyAddresses": [
                (
                    MODIFY_REPLACE,
                    ["".join(["SMTP:", data["login"], "@", data["domain"]])],
                ),
                (MODIFY_REPLACE, [proxy]),
            ],
        }
        result = c.modify(
            dn=data["ou"],
            changes=attributes,
        )
        if not result:
            msg = "ERROR: User '{0}' was not created: {1}".format(
                "".join([data["first"], " ", data["last"]]),
                c.result.get("description"),
            )
            raise Exception(msg)
    if data["password"].__len__() >= 8:
        c.extend.microsoft.modify_password(
            user=data["ou"], new_password=data["password"], old_password=None
        )
    self.progress["value"] = 100
    widgetStatus(self, NORMAL)
    self.status["text"] = "Idle..."
    # self.messageBox("SUCCESS!!", "User Updated!")
    Toast("SUCCESS!!", "User Updated!", "happy")
    self.progress["value"] = 0
    self.editSelect("E")
    # except:  # noqa
    #     self.status["text"] = "Idle..."
    #     widgetStatus(self, NORMAL)
    #     Toast("ERROR!!", "An error has occured!", "angry")
    #     # self.messageBox("ERROR!!", "An error has occured!")
    #     self.progress["value"] = 0


def createUser(self, data):
    # pythoncom.CoInitialize()
    # try:
    self.status["text"] = "".join(["Creating ", data["first"], " ", data["last"]])

    with ldap_connection(self) as c:
        attributes = {
            "SAMAccountName": data["login"],
            "givenName": data["first"],
            "userPrincipalName": "".join([data["login"], "@", data["domain"]]),
            "DisplayName": "".join([data["first"], " ", data["last"]]),
            "sn": data["last"],
            "mail": "".join([data["login"], "@", data["domain"]]),
            "proxyAddresses": [
                "".join(["SMTP:", data["login"], "@", data["domain"]]),
                "".join(["smtp:", data["login"], "@", data["proxy"]]),
            ],
            "HomeDirectory": data["homeDirectory"],
            "HomeDrive": data["homeDrive"],
            "title": data["title"],
            "description": data["description"],
            "department": data["department"],
            "company": data["company"],
            "pwdLastSet": 0,
        }
        user_dn = "".join(["CN=", data["first"], " ", data["last"], ",", self.posOU])
        result = c.add(
            dn=user_dn,
            object_class=["top", "person", "organizationalPerson", "user"],
            attributes=attributes,
        )
        if not result:
            msg = "ERROR: User '{0}' was not created: {1}".format(
                "".join([data["first"], " ", data["last"]]),
                c.result.get("description"),
            )
            raise Exception(msg)

    self.progress["value"] = 30
    c.extend.microsoft.unlock_account(user=user_dn)
    c.extend.microsoft.modify_password(
        user=user_dn, new_password=data["password"], old_password=None
    )
    # Enable account - must happen after user password is set
    # newuser.set_user_account_control_setting("DONT_EXPIRE_PASSWD", True)
    # newuser.set_user_account_control_setting("PASSWD_NOTREQD", False)
    enable_account = {"userAccountControl": (MODIFY_REPLACE, [UAC])}
    c.modify(user_dn, changes=enable_account)

    self.progress["value"] = 50
    self.status["text"] = "".join(
        ["Adding ", data["first"], " ", data["last"], " to groups"]
    )
    # print(data["groups"])
    c.extend.microsoft.add_members_to_groups([user_dn], data["groups"])
    # for gp in data["groups"]:
    #     newgroup = pyad_Trinity.adgroup.ADGroup.from_cn(gp)
    #     newuser.add_to_group(newgroup)
    self.progress["value"] = 80
    self.status["text"] = "".join(
        ["Creating ", data["first"], " ", data["last"], " home directory"]
    )
    # print(data["homeDirectory"])
    nHomeDir = checkNetworkAccess(self, data["homeDirectory"], data["login"])
    createHomeDir(
        data["login"],
        nHomeDir,
        base64.b64decode(self.domainName).decode("UTF-8").strip(),
    )
    self.progress["value"] = 100
    widgetStatus(self, NORMAL)
    self.status["text"] = "Idle..."
    # self.messageBox("SUCCESS!!", "User Created!")
    Toast("SUCCESS!!", "User Created!", "happy")
    self.progress["value"] = 0
    # except Exception as e:
    #     self.status["text"] = "Idle..."
    #     widgetStatus(self, NORMAL)
    #     self.progress["value"] = 0
    #     Toast("ERROR!!", "An error has occured!", "angry")
    #     self.messageBox("ERROR!!", e)


def createHomeDir(username, homeDir, domainName):
    print(homeDir)
    if path.exists(homeDir) is False:
        mkdir(homeDir)

        # user, domain, type = win32security.LookupAccountName(
        #     "", domainName + "\\" + username
        # )
        if name == "nt":
            user, domain, type = win32security.LookupAccountName(domainName, username)
            sd = win32security.GetFileSecurity(
                homeDir, win32security.DACL_SECURITY_INFORMATION
            )

            dacl = sd.GetSecurityDescriptorDacl()
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, 3, 2032127, user)

            # sd.SetSecurityDescriptorDacl(1, dacl, 0)
            sd.SetSecurityDescriptorDacl(dacl[0], True)
            win32security.SetFileSecurity(
                homeDir, win32security.DACL_SECURITY_INFORMATION, sd
            )


def checkNetworkAccess(self, homeDir, username):
    try:
        if path.exists(self.paths.get()):
            print(homeDir)
            return homeDir
        else:
            print(self.paths.get().replace("HCS-FS01", "192.168.3.35"))
            return "".join(
                [self.paths.get().replace("HCS-FS01", "192.168.3.35"), "\\", username]
            )
    except Exception as e:
        print(self.paths.get().replace("HCS-FS01", "192.168.3.35"))
        print(e)
        return "".join(
            [self.paths.get().replace("HCS-FS01", "192.168.3.35"), "\\", username]
        )


def remove_groups(self):
    # pythoncom.CoInitialize()
    try:
        userlist = listUsers(self, self.expiredOU)
        # group = listGroups(self, base64.b64decode(self.groupOU).decode("UTF-8"))
        maxs = userlist.__len__()
        self.status["text"] = "Loading Users..."
        userCount = 1
        for x in userlist:
            self.tree2.insert(
                "", "end", values=(x, userlist[x]["name"], userlist[x]["homeDir"])
            )
            self.progress["value"] = userCount
        count = 1
        self.progress["value"] = count
        self.status["text"] = "Cleaning Users: " + str(count) + "/" + str(maxs)
        self.progress["maximum"] = float(maxs)
        for y in userlist:
            count += 1
            self.progress["value"] = count
            # for x in group:
            #     removeGroups(self, userlist[y]["ou"], group[x]["ou"])
            self.status["text"] = "Cleaning Users: " + str(count) + "/" + str(maxs)
            removeHomedrive(userlist[y]["homeDir"])
            for child in self.tree2.get_children():
                if y in self.tree2.item(child)["values"]:
                    self.tree2.delete(child)
    except Exception as e:
        print(e)
        self.messageBox("ERROR!", "An error has occurred!")
    widgetStatus(self, NORMAL)
    self.status["text"] = "Idle..."
    self.after(1000, self.resetProgress)


def listUsers(self, ou):
    users = {}
    with ldap_connection(self) as c:
        status, result, response, _ = c.search(
            search_base=str(ou),
            search_filter="(&(objectClass=user)(objectCategory=person))",
            attributes=[
                "displayName",
                "distinguishedName",
                "sAMAccountName",
                "homeDirectory",
            ],
            search_scope=SUBTREE,
            get_operational_attributes=True,
        )
        if not result:
            msg = "ERROR: '{0}'".format(c.result.get("description"))
            raise Exception(msg)

        for x in response:
            res = x["attributes"]
            users[res["sAMAccountName"]] = {
                "name": res["displayName"],
                "ou": res["distinguishedName"],
                "homeDir": res["homeDirectory"],
            }
    return users


def listUsers2(self, ou):
    users = {}
    with ldap_connection(self) as c:
        status, result, response, _ = c.search(
            search_base=str(ou),
            search_filter="(&(objectClass=user)(objectCategory=person))",
            attributes=[
                "displayName",
                "distinguishedName",
                "sAMAccountName",
                "description",
                "title",
                "mail",
                "userPrincipalName",
                "sn",
                "givenName",
                "proxyAddresses",
            ],
            search_scope=SUBTREE,
            get_operational_attributes=True,
        )
        if not result:
            msg = "ERROR: '{0}'".format(c.result.get("description"))
            raise Exception(msg)

        for x in response:
            res = x["attributes"]
            users[res["sAMAccountName"]] = {
                "name": res["displayName"],
                "ou": res["distinguishedName"],
                "fname": res["givenName"],
                "lname": res["sn"],
                "description": res["description"],
                "title": res["title"],
                "mail": res["mail"],
                "userPrincipalName": res["userPrincipalName"],
                "proxyAddresses": res["proxyAddresses"],
            }
    return users


def removeGroups(self, users, groupOU):
    with ldap_connection(self) as c:
        removeUsersInGroups(c, users, groupOU, fix=True)


def removeHomedrive(paths):
    try:
        if path.exists(paths):
            removedirs(paths)
    except Exception as e:
        print(e)


def moveUser(self, bOU, aOU):
    self.progress["value"] = 60
    username = bOU.split(",")[0]
    with ldap_connection(self) as c:
        result = c.modify_dn(
            bOU,
            username,
            new_superior=aOU,
        )
        res = get_operation_result(c, result)
        if not res["description"] == "success":
            msg = (
                "unable to move user "
                + username.replace("CN=", "")
                + ": "
                + str(result)
            )
            raise Exception(msg)

    selected_item = self.tree3.selection()[0]
    self.tree3.delete(selected_item)
    self.progress["value"] = 100
    self.selItem2 = []
    self.status["text"] = "Idle..."
    # self.messageBox("SUCCESS!!", "Move Complete!")
    Toast("SUCCESS!!", "Move Complete!", "happy")
    widgetStatus(self, NORMAL)
    self.progress["value"] = 0
