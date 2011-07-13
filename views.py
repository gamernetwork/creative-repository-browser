from django.shortcuts import *
from django.http import *
from django.conf import settings

import re

from django.views.static import serve

import os

import pysvn
svnc = pysvn.Client()

def folder( request, path ):
    op = ""
    items = svnc.list( settings.CSVN_REPOS + path, depth=pysvn.depth.immediates )
    folder = items[ 0 ][ 0 ]
    folder.stack = []
    folder.basename = os.path.basename( folder.repos_path );
    print folder.repos_path
    for level in folder.repos_path.replace( "//", "/" )[1:].split( "/" ):
        print level 
        folder.stack.append(
            {
                "name": level,
                "path": "/" + "/".join(
                    [ l[ "name" ] for l in folder.stack + [ { "name": level, "path": level }, ] ]
                )
            }
        )
    items = items[ 1: ]
    folders = [
        item[ 0 ]# { 'basename' : os.path.basename( item[ 0 ].repos_path ) } )
        for item in items if item[ 0 ].kind == pysvn.node_kind.dir
    ]
    items = [
        item[ 0 ]#.update()# { 'basename' : os.path.basename( item[ 0 ].repos_path ) } )
        for item in items if item[ 0 ].kind == pysvn.node_kind.file
    ]
    for item in folders:
        item.update( { 'basename' : os.path.basename( item.repos_path ), 'repos_path': item.repos_path.replace( "//", "/" )[1:] } )
    for item in items:
        item.update(
            {
                'basename': os.path.basename( item.repos_path ),
                'repos_path': item.repos_path[1:],
                'thumbnail': re.sub( "\.[a-zA-Z0-9]+$", ".jpg", item.repos_path[1:] )
            }
        )
        if item[ 'basename' ].endswith( ( '.psd', '.jpg', '.jpeg', 'png', '.PSD', '.JPG', '.JPEG', 'PNG', ) ):
            item[ 'previewable' ] = True
        else:
            item[ 'previewable' ] = False
    
    return render( request, "folder.html", { "folder": folder, "folders": folders, "items": items } ) 

import datetime
def fileinfo( request, path ):
    def updatedate( log ):
        log.datetime =  datetime.datetime.fromtimestamp( log.date )
        return log

    log = svnc.log( settings.CSVN_REPOS + path )
    log = [
        updatedate( l ) for l in log
    ]
    return render( request, "info.html", { "path": path, "log": log } ) 

def getfile( request, path ):
    filename = os.path.basename( path )
    mime = svnc.propget( "svn:mime-type", settings.CSVN_REPOS + path ).itervalues().next()
    response = HttpResponse( mimetype = mime )
    response['Content-Disposition'] = 'attachment; filename=' + filename

    response.write( svnc.cat( settings.CSVN_REPOS + path ) )
    return response

# this might need tuning
def getconverted( request, path ):
    import subprocess
    filename = re.sub( "\.[a-zA-Z0-9]+$", ".jpg", os.path.basename( path ) )
    mime = svnc.propget( "svn:mime-type", settings.CSVN_REPOS + path ).itervalues().next()
    response = HttpResponse( mimetype = mime )
    response['Content-Disposition'] = 'attachment; filename=' + filename

    #s = subprocess.Popen( "/bin/ls", shell = True, stdout = subprocess.PIPE )
    s = subprocess.Popen( "/usr/bin/convert -[0] -quality 90 jpg:-", shell=True, stdin = subprocess.PIPE, stdout = subprocess.PIPE )
    #s.stdin.write( svnc.cat( settings.CSVN_REPOS + path ) )
    #response.write( svnc.cat( settings.CSVN_REPOS + path ) )
    response.write( s.communicate( input = svnc.cat( settings.CSVN_REPOS + path ) )[0] )
    #response.write( s.stdout )
    return response

def getthumbnail( request, path ):
    return serve( request, path, settings.THUMBNAIL_ROOT, False )
