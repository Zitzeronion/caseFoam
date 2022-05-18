"""CaseFOAM utility.

A set of utilities to use with CaseFOAM.

"""
import os
import PyFoam.RunDictionary.ParsedParameterFile as PPF
from typing import List

def mkRmCases(baseCase, cases, isWriteDir=False):
    """Make case remove file.

    Generates a bash script 'rmCases' to remove all cases and bring folder
    to original structure.

    Parameters
    ----------
    baseCase : string
        Path to the baseCase directory.
    cases : list
        List of parent, child and grandchild names.
    isWriteDir : bool
        If ``baseCase`` is a copy defined by ``writeDir``, only the
        ``writeDir`` will be removed.

    """
    with open('rmCases', 'w') as _rmCasesFile:
        # write script head
        _rmCasesFile.write('# Script to remove all cases and bring folder to '
                           'original structure\n')

        # bash command to remove cases
        for case in cases[0]:
            _rmCasesFile.write('rm -rf %s*\n' % os.path.join(baseCase, case))

        # bash command to rebuild original structure
        _rmCasesFile.write('\nmv %s %s\n' %
                           (os.path.join(baseCase, 'baseCase', '*'),
                            os.path.join(baseCase, '')))
        _rmCasesFile.write('rm -rf %s\n' % os.path.join(baseCase, 'baseCase'))
        _rmCasesFile.write('rm Allrun Allclean rmCases\n')

        if isWriteDir:
            _rmCasesFile.write(
                'while true; do\n'
                '    read -p "Delete %s directory? All changes in %s will be lost. [y/N] " yn\n'
                '    case $yn in\n'
                '        [Yy]* ) rm -rf %s; break;;\n'
                '        [Nn]* ) exit;;\n'
                '        * ) exit;;\n'
                '    esac\n'
                'done\n'
                % (baseCase, baseCase, baseCase)
            )
            _rmCasesFile.write('rm -rf %s\n' % baseCase)

    os.system('chmod +x rmCases')


def mkAllRunClean(baseCase):
    """Make Allrun and Allclean script.

    Generate a Allrun and Allclean script to run and clean all cases
    generated by CaseFOAM.

    Parameters
    ----------
    baseCase : string
        Path to the baseCase directory.

    """
    cases = list()
    for _root, _dirs, _files in os.walk(baseCase):
        for _file in _files:
            if _file.endswith('run') and 'baseCase' not in _root:
                cases.append(_root)

    # generate Allrun
    with open('Allrun', 'w') as _allrunFile:
        # write script head
        _allrunFile.write('# OpenFOAM Allrun script to run all cases generated'
                          ' by CaseFOAM\n\n')

        for case in cases:
            _allrunFile.write('%s/Allrun &\n' % case)

    # generate Allclean
    with open('Allclean', 'w') as _allcleanFile:
        # write script head
        _allcleanFile.write('# OpenFOAM Allclean script to clean all cases'
                            ' generated by CaseFOAM\n\n')

        for case in cases:
            _allcleanFile.write('%s/Allclean &\n' % case)

    os.system('chmod +x Allrun Allclean')


def getFileStructure(file):
    """Get the structure of OpenFOAM dictionary.

    Parameters
    ----------
    file : str
        Path to the OpenFOAM file.

    Returns
    -------
    fileStructure : dict
        Content of the OpenFOAM file as dictionary.

    Examples
    --------
    Get the file content and structure of a velocity file

    >>> casefoam.utility.getFileStructure('0/U')
    {'boundaryField': {'bottom': {'type': 'symmetryPlane'},
      'defaultFaces': {'type': 'empty'},
      'inlet': {'type': 'fixedValue', 'value': 'uniform (3 0 0)'},
      'obstacle': {'type': 'slip'},
      'outlet': {'inletValue': 'uniform (3 0 0)',
       'type': 'inletOutlet',
       'value': 'uniform (3 0 0)'},
      'top': {'type': 'symmetryPlane'}},
     'dimensions': '[ 0 1 -1 0 0 0 0 ]',
     'internalField': 'uniform (3 0 0)'}

    """
    fileStructure = PPF.ParsedParameterFile(file)
    return fileStructure.content


def _of_case(dirnames: List[str],filenames: List[str]) -> bool:
    """classify directory as OpenFOAM case

    Parameters
    ----------
    dirnames : List[str]
        list of directories in the folder
    filenames : List[str]
        list of files in the folder

    Returns
    ofcase : bool
        is the folder an OpenFOAM Case
    """
    if "constant" in dirnames and "system" in dirnames:
        return True
    return False


def of_cases(dir_name: str) -> List[str]:
    """list all OpenFOAM cases in folder

    Parameters
    ----------
    dir_name : str
        name of the search directory

    Returns
    ofcases : List[str]
        pathes of the OpenFOAM directories
    """
    cases = []
    for path, dirnames, filenames in os.walk(dir_name):
        if _of_case(dirnames,filenames):
            if "baseCase" not in path:
                cases.append(path)
            dirnames[:] = []
    return cases