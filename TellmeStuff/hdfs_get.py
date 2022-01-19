import sys, hmac, hashlib, base64, re, os,urllib, urllib2
from time import gmtime, strftime
from optparse import OptionParser

if __name__ == '__main__':

    parser = OptionParser(description='Copy files from hdfs to sv2. All files will be concatenated while copying.')
    parser.add_option("-s", "--source_hdfs_directory", action="store", dest="src_hdfs_dir",help="hdfs directory from which the files need to be copied", type="string")
    parser.add_option("-d", "--dest_sv2_directory",action="store", dest="dst_output_dir",help="sv2 directory where the files need to be copied", type="string")
    (options, args) = parser.parse_args()

    ## Proxy URL for sv2
    proxy = urllib2.ProxyHandler({'http': 'http://webproxy.cell.sv2.tellme.com:3128'})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)

    ## Create output directory if it doesn't exist
    if not os.path.exists(options.dst_output_dir):
        os.makedirs(options.dst_output_dir)

    x=re.compile(r"(http://datanode.*?browseDirectory\.jsp\?dir=).*?(&name.*?:8020)")
    sample_path=x.findall(urllib2.urlopen("http://namenode01.bigdata.va1.247-inc.net:50070/nn_browsedfscontent.jsp").read())[0]

    a=re.compile(r'nnaddr.*')
    datanode_path = sample_path[0]+options.src_hdfs_dir.replace("/","%2F")+sample_path[1]

    ## Get the number of files and file names
    filenames=re.compile("8020\">(part-[a-z]-)([0-9]+)</a>")
    sample_file_name,tot=filenames.findall(urllib2.urlopen(datanode_path).read())[-1]
    print 'Copying content from ' +str(int(tot)+1)+' hdfs files to '+ os.path.join(options.dst_output_dir,'query_output')

    ## Write to output files
    out_file = open(os.path.join(options.dst_output_dir,'query_output'), 'w')
    for i in range(int(tot)+1):
        out_file.write(urllib2.urlopen(sample_path[0].replace("browseDirectory.jsp?dir=","")+"streamFile"+options.src_hdfs_dir+'/'+sample_file_name+format(i,'05')+"?"+a.findall(sample_path[1])[0]).read())
    out_file.close()
