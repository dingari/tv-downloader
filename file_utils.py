import rarfile, shutil

from zipfile import ZipFile

class FileUtils:

    def __init__(self, rartool_path):
        self.rartool_path = rartool_path;
        rarfile.UNRAR_TOOL = self.rartool_path;

    # source:               Full path to file
    # dest:                 Path to destination directory
    # (opt) new_filename:   Optional new filename for extracted file
    def copy_file(self, source, dest, new_filename=None):
        #TODO: display progress
        print('Copying {} to {}'.format(source, dest));

        if(not os.path.exists(dest)):
            os.makedirs(dest);

        if(new_filename):
            new_filename = '{}.{}'.format(new_filename, re.search('.*\.(.*)$', source).groups()[0]);
            dest = os.path.join(dest, new_filename);

        shutil.copy(source, dest);


    # source:               Path to directory containing archives
    # dest:                 Path to destination directory
    # (opt) new_filename:   Optional new filename for extracted file
    def extract_file(self, source, dest, new_filename=None):
        files = os.listdir(source);

        rarfiles = (f for f in files if re.match('.*\.rar', f));
        filepath = os.path.join(source, next(rarfiles));

        rf = rarfile.RarFile(filepath);

        the_file = filename = rf.namelist().pop();

        if(new_filename):
            (ext, ) = re.search('.*\.(.*)$', the_file).groups();
            the_file = '{}.{}'.format(new_filename, ext);
        else:
            the_file = filename;

        print('Extracting', filename, 'to', os.path.join(dest, the_file))
        rf.extract(filename, dest);

        old_path = os.path.join(dest, filename);
        new_path = os.path.join(dest, the_file);
        os.rename(old_path, new_path);


