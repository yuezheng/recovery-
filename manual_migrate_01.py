
def argsParser(commandArgs):
    import sys,getopt
    opts, args = getopt.getopt(sys.argv[1:], "i:h:t:")
    InfoList = []
    for k,v in opts:
        if k == '-i':
            InfoList.append(v)
        if k == '-h':
            InfoList.append(v)
        if k == '-t':
            InfoList.append(v)
    return InfoList

def updataDB(instanceID,destHost):
    import MySQLdb
    try:
        conn=MySQLdb.connect(host='192.168.241.12',user='nova',passwd='password',db='nova',port=3306)
        cur = conn.cursor()
        if cur.execute("update instances set host ='%s' where uuid = '%s'" % (destHost,instanceID)):
            conn.commit()
            return 1
        else :
            return 0
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    finally:
        cur.close()
        conn.close()


def getInstanceInHex(instanceID):
    '''get in from database ,and transfer to hex  '''
    import MySQLdb
    ID = 0
    try:
        conn=MySQLdb.connect(host='192.168.241.12',user='nova',passwd='password',db='nova',port=3306)
        cur = conn.cursor()
        cur.execute("select id,display_name from instances where uuid = '%s'" % instanceID)
        Info = cur.fetchone()
        HexID = hex(int(Info[0]))
        display_name = Info[1]
        shortHexID = HexID[2:]
        instanceName = 'instance-' + shortHexID.zfill(8)
        return (instanceName,display_name)
    except MySQLdb.Error,e:
        print "Mysql Error %d :%s" % (e.args[0],e.args[1])
    finally:
        cur.close()
        conn.close()


def getFirewallName(instanceName):
    from xml.dom import minidom
    filePath = '/var/lib/nova/instances/%s/libvirt.xml' % instanceName
    xmldoc = minidom.parse(filePath)
    filterref = xmldoc.getElementsByTagName('filterref')
    filter = filterref[0].attributes['filter'].value
    print filter    
    return filter


def createFirewall(filterName):
    import os 
    filterUUIDO = os.popen('uuidgen %s' % filterName).read()
    filterUUID = filterUUIDO[:-1] 
    print "filteruuid is :%s" % filterUUID 
    firewallFile = file('/etc/libvirt/nwfilter/%s.xml' % filterName,'w')
    
    line1 = "<filter name='%s' chain='root'>\n" % filterName
    line2 = "  <uuid>%s</uuid>\n" % filterUUID
    line3 = "  <filterref filter='nova-base'/>\n"
    line4 = "</filter>"
    lines = [line1,line2,line3,line4]

    for line in lines:
        print line
        firewallFile.write(line)

    firewallFile.close()
    
    checkXMLFile = file('/etc/libvirt/nwfilter/%s.xml' % filterName,'r')
    print 'The XML file is :'
    for line in checkXMLFile.readlines():
        print line
    checkXMLFile.close()
#    os.popen(createFilterFile)
    

def getMacAndIp(instanceName):
    import re
    filterfile = file('/var/lib/nova/instances/%s/libvirt.xml' % instanceName,'r')
    content = filterfile.readlines()
    macLine = ''
    IPLine = ''
    for line in content:
        if 'mac' in line:
            macLine = line
        elif 'IP' in line:
            IPLine = line

    pattanGetMac = re.compile(r'address\s*=\s*\'(.+)\'')
    pattanGetIP = re.compile(r'value\s*=\s*\"(.+)\"')
    searchMac = pattanGetMac.search(macLine)
    searchIP = pattanGetIP.search(IPLine)
    mac = searchMac.group(1)
    IP = searchIP.group(1)
    address = {'Mac':mac,'IP':IP}
    return address

def getTenantNameByInstanceID(instanceID):
    import MySQLdb
    project_id = ''
    tenant_name = ''
    try:
        conn = MySQLdb.connect(host='192.168.241.12',user='nova',passwd='password',db='nova',port=3306)
        cur = conn.cursor()
        cur.execute("select project_id from instances where uuid = '%s'" % instancesID)
        project_id = cur.fetchone()
    except MySQLdb.Error,e:
        print "Mysql Error %d :%s" % (e.args[0],e.args[1])
    finally:
        cur.close()
        conn.close()

    try:
        conn = MySQLdb.connect(host='192.168.241.12',user='keystone',passwd='password',db='keystone',port=3306)
        cur = conn.cursor()
        cur.execute("select name from tenant where id = '%s'" % project_id)
        tenant_name = cur.fetchone()
    except MySQLdb.Error,e:
        print "Mysql Error %d :%s" % (e.args[0],e.args[1])
    finally:
        cur.close()
        conn.close()

    return tenant_name


def updateVMConf(displayName,instanceMac,instanceIP,instanceTenantName):
    line = '\n%s,%s.novalocal,%s' % (instanceMac,displayName,instanceIP)
    confFile = '/var/lib/nova/networks/nova-br%s.conf' % instanceTenantName 
    conf = file(confFile,'a')
    conf.write(line)
    conf.close()

    chackConf = file(confFile,'r')
    lines = chackConf.readlines()
    for line in lines:
        print line
    chackConf.close() 

def linkLibvirt(instanceName):
    import os
    print os.popen('/etc/init.d/libvirt-bin restart')
    print os.popen('cd /var/lib/nova/instances/%s/ ;virsh define libvirt.xml;virsh start %s' % (instanceName,instanceName)) 

def main():
    args = sys.argv[1:]
    INFO = argsParser(args)
    instanceID = INFO[0]
    destHost = INFO[1]
    instanceTenantName = INFO[2]
    
    if updataDB(instanceID,destHost):
        print 'Change Database complate'
        instanceNameAndDisplayName = getInstanceInHex(instanceID)
        instanceName = instanceNameAndDisplayName[0]
        displayName = instanceNameAndDisplayName[1]
        print 'this instance name is :%s  DisplayName=%s' % (instanceName,displayName)
        filterW = getFirewallName(instanceName)
        print 'this instance firewall filter is :%s' % filterW
        createFirewall(filterW)
        address = getMacAndIp(instanceName)
        instanceMac = address['Mac']
        instanceIP = address['IP']
        print 'this instance mac is : %s \n ip is :%s' %(instanceMac,instanceIP)
#       instanceTenantName = getTenantNameByInstanceID(instanceID)
        updateVMConf(displayName,instanceMac,instanceIP,instanceTenantName)
        linkLibvirt(instanceName)
    else :
        print 'Change Database Failed!'


if __name__ == "__main__":
    main()
