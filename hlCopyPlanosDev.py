#!/usr/bin/python3

import os, sys, stat, signal, re, fnmatch
import glob, itertools, json, hashlib, codecs
from os import listdir
from os.path import isfile, join
from datetime import datetime

fpLogs = None

totalArquivos = 0
totalBytes = 0

def writeLog(logLine):
  global fpLogs 
  print( logLine )

  if fpLogs != None:
    fpLogs.write(f"{logLine}\n")

# retorna as informacoes de um arquivo
def getFileInfo(filePath):
  entry = {}
  entry['name'] = ''
  entry['path'] = ''
  entry['md5hash'] = ''
  entry['ST_INO'] = 0
  entry['ST_DEV'] = 0
  entry['ST_NLINK'] = 0
  entry['ST_SIZE'] = 0
  entry['ST_MTIME'] = 0

  try:
    if isinstance(filePath, dict):
      if 'name' in filePath:
        entry['name'] = filePath['name']
      if 'path' in filePath:
        entry['path'] = filePath['path']
      if 'md5hash' in filePath:
        entry['md5hash'] = filePath['md5hash']
      if 'ST_INO' in filePath:
        entry['ST_INO'] = filePath['ST_INO']
      if 'ST_DEV' in filePath:
        entry['ST_DEV'] = filePath['ST_DEV']
      if 'ST_NLINK' in filePath:
        entry['ST_NLINK'] = filePath['ST_NLINK']
      if 'ST_SIZE' in filePath:
        entry['ST_SIZE'] = filePath['ST_SIZE']
      if 'ST_MTIME' in filePath:
        entry['ST_MTIME'] = filePath['ST_MTIME']
    else:
      fullPath = os.path.abspath(filePath)
      entry['name'] = os.path.basename(fullPath)  
      entry['path'] = fullPath.replace(entry['name'],'')
      fileStat = os.stat(fullPath)
      entry['ST_INO'] = fileStat[stat.ST_INO]
      entry['ST_DEV'] = fileStat[stat.ST_DEV]
      entry['ST_NLINK'] = fileStat[stat.ST_NLINK]
      entry['ST_SIZE'] = fileStat[stat.ST_SIZE]
      entry['ST_MTIME'] = fileStat[stat.ST_MTIME]
  except OSError as err:
    writeLog( f"exception ({err}) in getFileInfo: {filePath}")      
  else:
    return entry

  return None

def signal_handler(sig, frame):
  writeLog( "signal_handler!!")

  finalProc()

signal.signal(signal.SIGINT, signal_handler)

def finalProc():
  global fpLogs, totalArquivos, totalBytes

  writeLog(f"\nTotais: \ntotal arquivos:{totalArquivos:,} : total bytes:{totalBytes:,}")

  if fpLogs != None:
    fpLogs.close()


# processa diretorios: dictParms['s','d','r','w','l','if','id','xf','xd','ST_DEV']
def HardLinkCopy(dictParams,folder=""):
  global totalArquivos, totalBytes  
  
  if False == isinstance(dictParams, dict):
    print( f"ERROR: parametro informado não é um dicionário!")
    return

  while len(folder)> 0 and folder[0:1] in ['\\','/']:
    folder = folder[1:]

  srcPath = join(dictParams['s'], folder)
  
  if len(dictParams['d']) > 0:
    dstPath = join(dictParams['d'], folder)
  else:
    dstPath = ""

  #print( f"->folder: '{folder}' : srcPath: '{srcPath}' : dstPath: '{dstPath}'" )

  fIncludeFolder = False
  # processa a lista de diretórios a incluir
  if len(dictParams['id']) > 0:
    for wildcard in dictParams['id']:
      if fnmatch.fnmatch(folder.lower(), wildcard.lower()):
        writeLog(f"folder:'{folder}' match id:'{wildcard}'")
        fIncludeFolder = True

  # processa a lista de diretórios a excluir
  if False == fIncludeFolder and len(dictParams['xd']) > 0:
    for wildcard in dictParams['xd']:
      if fnmatch.fnmatch(folder.lower(), wildcard.lower()):
        writeLog(f"folder:'{folder}' match xd:'{wildcard}'")
        return

  if len(dictParams['d']) > 0:
    dest = join(dstPath,folder)
    if False == os.path.exists(dest):
      os.makedirs(dest)

  #writeLog( f"folder: '{folder}' | srcPath: '{srcPath}' | dstPath: '{dstPath}'")

  for pathName in itertools.chain(glob.iglob(join(srcPath, '.**')), glob.iglob(join(srcPath, '**'))):

    #writeLog( f"pathName: '{pathName}' | isfile: '{isfile(pathName)}' ")

    if isfile(pathName):
      fXf = False
      fIf = True

      if len(dictParms['if']) > 0:
        fIf = False
        for wildcard in dictParms['if']:
          #print( f"if: pathName: '{pathName.lower()}' | wildcard: '{wildcard.lower()}' | fnmatch: {fnmatch.fnmatch(pathName.lower(), wildcard.lower())}")

          if fnmatch.fnmatch(pathName.lower(), wildcard.lower()):
            #print(f"file:'{pathName}' match if:'{wildcard}'")
            fIf = True
            break
      elif len(dictParams['xf']) > 0:
        fXf = False
        for wildcard in dictParms['xf']:
          #print( f"xf: pathName: '{pathName.lower()}' | wildcard: '{wildcard.lower()}' | fnmatch: {fnmatch.fnmatch(pathName.lower(), wildcard.lower())}")
          
          if fnmatch.fnmatch(pathName.lower(), wildcard.lower()):
            #print(f"file:'{pathName}' match xf:'{wildcard}'")
            fXf = True
            break

      if True == fIf and False == fXf:
        fInfo = getFileInfo(pathName)
        
        #print( f"fInfo['ST_DEV'] == dictParams['ST_DEV']: {fInfo['ST_DEV'] == dictParams['ST_DEV']}")

        if fInfo['ST_DEV'] == dictParams['ST_DEV']:
          totalArquivos += 1
          totalBytes += fInfo['ST_SIZE']
          writeLog(f"file:'{pathName}' : len:{fInfo['ST_SIZE']:,} : nLinks:{fInfo['ST_NLINK']} : qtd arquivos:{totalArquivos:,} : total bytes:{totalBytes:,}")

          if len(dictParams['d']) > 0:
            dest = join(dstPath,folder)
            newPathName = join(dest,os.path.basename(pathName))
            #print(f"copy '{pathName}' -> '{newPathName}'")
            try:  
              if os.path.exists(newPathName) and dictParms['w']:
                os.remove(newPathName)
              
              if False == os.path.exists(newPathName):
                os.link(pathName, newPathName)

            except OSError as err:
              writeLog( f"exception ({err}) ao criar o link: {newPathName}")

    else:
      #print(f"dictParms['r'] and False == fnmatch.fnmatch(pathName.lower(), dstPath.lower()):{dictParms['r'] and False == fnmatch.fnmatch(pathName.lower(), dstPath.lower())}")

      if dictParms['r'] and False == fnmatch.fnmatch(pathName.lower(), dstPath.lower()):
        dirname = pathName.replace(dictParams['s'],'')
        HardLinkCopy(dictParms, dirname)

# main
if __name__ == '__main__':
  
  waitingVlr = "s"
  msg = ""

  dictParms = {}
  dictParms['l'] = True
  dictParms['w'] = True
  dictParms['s'] = os.path.abspath("./planos")
  dictParms['d'] = os.path.abspath("../phpMsqlPhpadminDocker/www/atendimentos/planos")
  
  # os.path.abspath("../atendimentos/planos")

  dictParms['r'] = False
  dictParms['if'] = []
  dictParms['id'] = []
  dictParms['xf'] = []
  dictParms['xd'] = []
  dictParms['ST_DEV'] = getFileInfo(dictParms['s'])['ST_DEV']

  if len(sys.argv) > 1:

    for i in range(len(sys.argv)-1):
      arg = sys.argv[i+1]

      if len(arg) <= 3 and arg[0:1] == '-':
        if arg == '-s':
          waitingVlr = 's'
        elif arg == '-d':
          waitingVlr = 'd'
        elif arg == '-if':
          waitingVlr = 'if'
        elif arg == '-id':
          waitingVlr = 'id'
        elif arg == '-xf':
          waitingVlr = 'xf'
        elif arg == '-xd':
          waitingVlr = 'xd'
        elif arg == '-w':
          dictParms['w'] = True
        elif arg == '-r':
          dictParms['r'] = True
        elif arg == '-l':
          dictParms['l'] = True
        else:
          msg += f"\n* parâmetro desconhecido: '{arg}'"
      else:
        if waitingVlr == 's':
          fullpathArg = os.path.abspath(arg)
          if( True == os.path.exists(fullpathArg) and True == os.path.isdir(fullpathArg) ):
            dictParms['s'] = fullpathArg
            while len(dictParms['s'])> 0 and dictParms['s'][-1:] in ['\\','/']:
              dictParms['s'] = dictParms['s'][0:-1]
            dictParms['ST_DEV'] = getFileInfo(fullpathArg)['ST_DEV']
          else:
            msg += f"\n* folder de origem não existe: '{fullpathArg}"
        elif waitingVlr == 'd':
          dictParms['d'] = os.path.abspath(arg)
          while len(dictParms['d'])> 0 and dictParms['d'][-1:] in ['\\','/']:
            dictParms['d'] = dictParms['d'][0:-1]
        elif waitingVlr in ['if', 'id', 'xf', 'xd']:
          dictParms[waitingVlr].append(arg)
  
  if len(dictParms['s']) == 0 or (dictParms['w'] == True and len(dictParms['d']) == 0) or len(msg) > 0: 
    
    if len(msg) > 0:
      print( msg )
    
    if len(dictParms['s']) == 0:
      print( "* o folder de origem precisa ser informado")

    if len(dictParms['d']) > 0:
      if False == os.path.exists(dictParms['d']):
        os.mkdir( dictParms['d'] )
      if dictParms['ST_DEV'] != getFileInfo(dictParms['d'])['ST_DEV']:
        print("* os folders devem estar no mesmo disco")
      if( True != os.path.isdir(dictParms['d']) ):
        print( f"* o caminho de destino não é um folder ({dictParms['d']})" )
  
    print( 'use: ')
    print( sys.argv[0], '[-r]', '[-w]', '[-l]', '[-s path]', '[-d path]', '[-if wildcard_list]', '[-id wildcard_list]', '[-xf wildcard_list]', '[-xd wildcard_list]' )
    print( " -r -> se informado, a busca pelos arquivos de origem será recursiva")
    print( " -w -> se informado, os arquivos que já existirem no distino serão re-escritos")
    print( " -l -> se informado, será gravado um log das ações tomadas pelo app")
    print( " -s -> path do diretório de origem")
    print( " -d -> path do diretório de destino")
    print( " -if-> lista de filtros para os tipos de arquivos que devem ser copiados")
    print( " -id-> lista de filtros para os nomes de subdiretórios que devem ser copiados")
    print( " -xd-> lista de filtros, que deve estar entre aspas duplas e separados por espaços," )
    print( "       para os subdiretórios que não devem ser copiados")
    print( " -xf-> lista de filtros para os arquivos que não devem ser copiados")
    print( "  * ")
    print( "  * todos os filtros deve estar entre aspas e separados por espaços")
    print( "  * ")
    exit(1)
  
  outFileName = dictParms['s'].replace('/','_').replace(':','_').replace('\\','_').replace(' ','').replace('.','_')
  logsPath =  os.path.abspath('./logs')
  
  if True == dictParms['l']: 
    if False == os.path.exists(logsPath):
      os.mkdir( logsPath )

    outLogPath = os.path.join( logsPath, outFileName + '.log')
    fpLogs = codecs.open(outLogPath, 'w', "utf-8")

  HardLinkCopy(dictParms)
  finalProc()
  exit(1)
  