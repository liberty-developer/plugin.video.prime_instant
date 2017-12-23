
from __future__ import unicode_literals
import urllib
import urlparse
import urllib2
import hashlib
import socket
import mechanize
import cookielib
import sys
import re
import os
import platform
import json
import time
import string
import random
import shutil
import subprocess
import base64
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
from HTMLParser import HTMLParser
import resources.lib.ScrapeUtils as ScrapeUtils
import gzip
from StringIO import StringIO
import binascii

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
addonFolder = downloadScript = xbmc.translatePath('special://home/addons/'+addonID).decode('utf-8')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID).decode('utf-8')

icon = os.path.join(addonFolder, "icon.png")#.encode('utf-8')


def translation(id):
    return addon.getLocalizedString(id) #.encode('utf-8')

if not os.path.exists(os.path.join(addonUserDataFolder, "settings.xml")):
    xbmc.executebuiltin(unicode('XBMC.Notification(Info:,'+translation(30081)+',10000,'+icon+')').encode("utf-8"))
    addon.openSettings()

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
cj = cookielib.MozillaCookieJar()
downloadScript = os.path.join(addonFolder, "download.py").encode('utf-8')
downloadScriptTV = os.path.join(addonFolder, "downloadTV.py").encode('utf-8')
cacheFolder = os.path.join(addonUserDataFolder, "cache")
cacheFolderCoversTMDB = os.path.join(cacheFolder, "covers")
cacheFolderFanartTMDB = os.path.join(cacheFolder, "fanart")
addonFolderResources = os.path.join(addonFolder, "resources")
defaultFanart = os.path.join(addonFolderResources, "fanart.png")
libraryFolder = os.path.join(addonUserDataFolder, "library")
libraryFolderMovies = os.path.join(libraryFolder, "Movies")
libraryFolderTV = os.path.join(libraryFolder, "TV")
debugFile = os.path.join(addonUserDataFolder, "debug")
preferAmazonTrailer = addon.getSetting("preferAmazonTrailer") == "true"
showNotification = addon.getSetting("showNotification") == "true"
showOriginals = addon.getSetting("showOriginals") == "true"
showLibrary = addon.getSetting("showLibrary") == "true"
showAvailability = addon.getSetting("showAvailability") == "true"
showPaidVideos = addon.getSetting("showPaidVideos") == "true"
showKids = addon.getSetting("showKids") == "true"
forceView = addon.getSetting("forceView") == "true"
updateDB = addon.getSetting("updateDB") == "true"
useTMDb = addon.getSetting("useTMDb") == "true"
useWLSeriesComplete = addon.getSetting("useWLSeriesComplete") == "true"
watchlistOrder = addon.getSetting("watchlistOrder")
watchlistOrder = ["DATE_ADDED_DESC", "TITLE_ASC"][int(watchlistOrder)]
watchlistTVOrder = addon.getSetting("watchlistTVOrder")
watchlistTVOrder = ["DATE_ADDED_DESC", "TITLE_ASC"][int(watchlistTVOrder)]
selectLanguage = addon.getSetting("selectLanguage")
siteVersion = addon.getSetting("siteVersion")
apiMain = ["atv-ps", "atv-ps-eu", "atv-ps-eu", "atv-ps-fe"][int(siteVersion)]
marketplaceId=["ATVPDKIKX0DER", "A1F83G8C2ARO7P", "A1PA6795UKMFR9", "A1VC38T7YXB528"][int(siteVersion)]
siteVersionsList = ["com", "co.uk", "de", "co.jp"]
siteVersion = siteVersionsList[int(siteVersion)]
viewIdMovies = addon.getSetting("viewIdMovies")
viewIdShows = addon.getSetting("viewIdShows")
viewIdSeasons = addon.getSetting("viewIdSeasons")
viewIdEpisodes = addon.getSetting("viewIdEpisodes")
viewIdDetails = addon.getSetting("viewIdDetails")
urlMainS = "https://www.amazon."+siteVersion
urlMain = "http://www.amazon."+siteVersion
recourceMain = 'https://' + apiMain + '.amazon.' + siteVersion
addon.setSetting('email', '')
addon.setSetting('password', '')

cookieFile = os.path.join(addonUserDataFolder, siteVersion + ".cookies")

NODEBUG = False #True

HTTPCookieHandler = urllib2.HTTPCookieProcessor(cj)
HTTPSHandler = urllib2.HTTPSHandler(0)

opener = urllib2.build_opener(HTTPSHandler, HTTPCookieHandler)
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
opener.addheaders = [('User-agent', userAgent), ('Accept-encoding', 'gzip')]

def index():
    loginResult = login()
    if loginResult=="prime" or loginResult=="noprime":
        addDir(translation(30002), "", 'browseMovies', "")
        addDir(translation(30003), "", 'browseTV', "")
        xbmcplugin.endOfDirectory(pluginhandle)
    # elif loginResult=="noprime":
    #     listOriginals()
    elif loginResult=="none":
        xbmc.executebuiltin(unicode('XBMC.Notification(Info:,'+translation(30082)+',10000,'+icon+')').encode("utf-8"))


def browseMovies():
    addDir(translation(30004), urlMain+"/gp/video/watchlist/movie/?ie=UTF8&show=all&sort="+watchlistOrder, 'listWatchList', "")
    if showLibrary:
        addDir(translation(30005), urlMain+"/gp/video/library/movie?ie=UTF8&show=all&sort="+watchlistOrder, 'listWatchList', "")
    if siteVersion=="de":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&bbn=3010075031&field-entity_type=9739119031&field-ways_to_watch=7448695031&node=3010075031&pf_rd_i=home&pf_rd_m=A3JWKAKR8XB7XF&pf_rd_p=1381578687&pf_rd_r=DNQ8P36Q8CZGX71BH09Y&pf_rd_s=center-11&pf_rd_t=12401&search-alias=instant-video", 'listMovies', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "movie")
        addDir(translation(30014), "", 'listDecadesMovie', "")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A3010075031%2Cn%3A!3010076031%2Cn%3A3015915031%2Cp_n_theme_browse-bin%3A3015972031%2Cp_85%3A3282148031&ie=UTF8", 'listMovies', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031&sort=date-desc-rank", 'listMovies', "")
        addDir(translation(30009), urlMain+"/s/?n=4963842031&_encoding=UTF", 'listMovies', "")
        addDir(translation(30999), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010075031%2Cn%3A3356018031%2Cn%3A4225009031&sort=popularity-rank", 'listMovies', "")
    elif siteVersion=="com":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A2858778011%2Cn%3A7613704011&sort=popularity-rank", 'listMovies', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613704011&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "movie")
        addDir(translation(30012), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613704011&pickerToList=feature_five_browse-bin&ie=UTF8", 'listGenres', "", "movie")
        addDir(translation(30013), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613704011&pickerToList=feature_six_browse-bin&ie=UTF8", 'listGenres', "", "movie")
        addDir(translation(30014), "", 'listDecadesMovie', "")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_theme_browse-bin%3A2650365011&ie=UTF8", 'listMovies', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A2858778011%2Cn%3A7613704011&sort=date-desc-rank", 'listMovies', "")
    elif siteVersion=="co.uk":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010085031%2Cn%3A3356010031&sort=popularity-rank", 'listMovies', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "movie")
        addDir(translation(30014), "", 'listDecadesMovie', "")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_theme_browse-bin%3A3046745031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010085031%2Cn%3A3356010031&sort=date-desc-rank", 'listMovies', "")
    addDir(translation(30015), "movies", 'search', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def browseTV():
    addDir(translation(30004), urlMain+"/gp/video/watchlist/tv/?ie=UTF8&show=all&sort="+watchlistTVOrder, 'listWatchList', "")
    if showLibrary:
        addDir(translation(30005), urlMain+"/gp/video/library/tv/?ie=UTF8&show=all&sort="+watchlistTVOrder, 'listWatchList', "")
    if siteVersion=="de":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010075031%2Cn%3A3356019031&sort=popularity-rank", 'listShows', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356019031&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A3010075031%2Cn%3A!3010076031%2Cn%3A3015916031%2Cp_n_theme_browse-bin%3A3015972031%2Cp_85%3A3282148031&ie=UTF8", 'listShows', "")
        addDir(translation(30010), urlMain+"/gp/search/ajax/?_encoding=UTF8&keywords=[OV]&rh=n%3A3010075031%2Cn%3A3015916031%2Ck%3A[OV]%2Cp_85%3A3282148031&sort=date-desc-rank", 'listShows', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&bbn=3279204031&rh=n%3A3279204031%2Cn%3A3010075031%2Cn%3A3015916031&sort=date-desc-rank", 'listShows', "")
        addDir(translation(30999), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010075031%2Cn%3A3356019031%2Cn%3A4225009031&sort=popularity-rank", 'listShows', "")
    elif siteVersion=="co.jp":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A2858778011%2Cn%3A7613705011&sort=popularity-rank", 'listShows', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613705011&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        addDir(translation(30012), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613705011&pickerToList=feature_five_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        addDir(translation(30013), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613705011&pickerToList=feature_six_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613705011%2Cp_n_theme_browse-bin%3A2650365011&sort=csrank&ie=UTF8", 'listShows', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A2858778011%2Cn%3A7613705011&sort=date-desc-rank", 'listShows', "")
    elif siteVersion=="com":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A2858778011%2Cn%3A7613705011&sort=popularity-rank", 'listShows', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613705011&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        addDir(translation(30012), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613705011&pickerToList=feature_five_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        addDir(translation(30013), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613705011&pickerToList=feature_six_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613705011%2Cp_n_theme_browse-bin%3A2650365011&sort=csrank&ie=UTF8", 'listShows', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A2858778011%2Cn%3A7613705011&sort=date-desc-rank", 'listShows', "")
    elif siteVersion=="co.uk":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010085031%2Cn%3A3356011031&sort=popularity-rank", 'listShows', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356011031&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356011031%2Cp_n_theme_browse-bin%3A3046745031&sort=popularity-rank&ie=UTF8", 'listShows', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010085031%2Cn%3A3356011031&sort=date-desc-rank", 'listShows', "")
    if showOriginals:
        addDir("Amazon Originals: Pilot Season 2015", "", 'listOriginals', "")
    addDir(translation(30015), "tv", 'search', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listDecadesMovie():
    if siteVersion=="de":
        addDir(translation(30016), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289642031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30017), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289643031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30018), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289644031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30019), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289645031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30020), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289646031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30021), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289647031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30022), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289648031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
    elif siteVersion=="com":
        addDir(translation(30016), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651255011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30017), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651256011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30018), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651257011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30019), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651258011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30020), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651259011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30021), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651260011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30022), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651261011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
    elif siteVersion=="co.uk":
        addDir(translation(30016), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289666031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30017), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289667031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30018), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289668031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30019), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289669031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30020), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289670031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30021), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289671031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30022), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289672031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listOriginals():
    content = ""
    if siteVersion=="de":
        content = getUnicodePage(urlMain+"/b/?ie=UTF8&node=5457207031")
    elif siteVersion=="co.jp":
        content = getUnicodePage(urlMain+"/b/?ie=UTF8&node=3535604051")
    elif siteVersion=="com":
        content = getUnicodePage(urlMain+"/b/?ie=UTF8&node=9940930011")
    elif siteVersion=="co.uk":
        content = getUnicodePage(urlMain+"/b/?ie=UTF8&node=5687760031")
    #debug(content)
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    content = content[content.find('<map name="pilots'):]
    content = content[:content.find('</map>')]
    #spl = content.split('shape="rect"')
    thumbs = {}
    thumbs['maninthehighcastle'] = 'http://ecx.images-amazon.com/images/I/5114a5G6oQL.jpg'
    thumbs['cocked'] = 'http://ecx.images-amazon.com/images/I/51ky16-xESL.jpg'
    thumbs['maddogs'] = 'http://ecx.images-amazon.com/images/I/61mWRYn7U2L.jpg'
    thumbs['thenewyorkerpresents'] = 'http://ecx.images-amazon.com/images/I/41Yb8SUjMzL.jpg'
    thumbs['pointofhonor'] = 'http://ecx.images-amazon.com/images/I/51OBmT5ARUL.jpg'
    thumbs['downdog'] = 'http://ecx.images-amazon.com/images/I/51N2zkhOxGL.jpg'
    thumbs['salemrogers'] = 'http://ecx.images-amazon.com/images/I/510nXRWkoaL.jpg'
    thumbs['table58'] = 'http://ecx.images-amazon.com/images/I/51AIPgzNiWL.jpg'
    thumbs['buddytechdetective'] = 'http://ecx.images-amazon.com/images/I/513pbjgDLYL.jpg'
    thumbs['sarasolvesit'] = 'http://ecx.images-amazon.com/images/I/51Y5G5RbLUL.jpg'
    thumbs['stinkyanddirty'] = 'http://ecx.images-amazon.com/images/I/51WzytCUmdL.jpg'
    thumbs['niko'] = 'http://ecx.images-amazon.com/images/I/51XjJrg9JLL.jpg'
    thumbs['justaddmagic'] = 'http://ecx.images-amazon.com/images/I/5159YFd0hQL.jpg'
    pilotsmatch = re.compile('<area.+?alt="(.+?)".+?href="(.+?)"', re.DOTALL).findall(content)
    for pilotval in pilotsmatch:
        match = re.compile("/gp/product/(.+?)/", re.DOTALL).findall(pilotval[1])
        videoID = match[0]
        title = pilotval[0]
        title = cleanTitle(title)
        titleT = title.lower().replace(' ', '').strip()
        titleT = titleT.replace("pointofhonour", "pointofhonor")
        titleT = titleT.replace("buddytechdective", "buddytechdetective")
        titleT = titleT.replace("buddytechdetectives", "buddytechdetective")
        titleT = titleT.replace("thestinkyanddirtyshow", "stinkyanddirty")
        titleT = titleT.replace("nikkoandtheswordoflight", "niko")
        titleT = titleT.replace("nikoandtheswordoflight", "niko")
        thumb = ""
        if titleT in thumbs:
            thumb = thumbs[titleT]
        addShowDir(title, videoID, "listSeasons", thumb, "tv", showAll=True)
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode(500)')

def listWatchList(url):
    content = getUnicodePage(url)
    debug("listWatchList")
    #debug(content)
    #fp = open(os.path.join(addonFolder, "videolib.html"), "r")
    #content = unicode(fp.read(), "iso-8859-15")
    #fp.close()
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    showEntries = []
    items = []
    dlParams = []
    videoType = None
    delim = ''
    oldstyle = False

    if '<div class="a-section' in content:
        delim = '<div class="a-section'
        beginarea = content.find(delim)
        area = content[beginarea:content.find('<div id="aiv-cl-main-bottom">', beginarea)]
    elif '<div class="grid-list-item' in content:
        delim = '<div class="grid-list-item'
        beginarea = content.find(delim)
        area = content[beginarea:content.find('<div id="navFooter">', beginarea)]
    elif '<div class="lib-item"' in content:
        delim = '<div class="lib-item"'
        beginarea = content.find(delim)
        area = content[beginarea:content.find('</table>', beginarea)]
    else:
        delim = '<div class="innerItem"'
        beginarea = content.find(delim)
        area = content[beginarea:]
    itemc = area.count(delim)

    for i in range(0, itemc, 1):
        if (i < itemc):
            elementend = area.find(delim, 1)
            items.append(area[:elementend])
            area = area[elementend:]
        else:
            items.append(area)
    for i in range(0, len(items), 1):
        entry = items[i]

        if oldstyle:
            entry = entry[:entry.find('</td>')]
        if "/library/" in url or ("/watchlist/" in url and ('class="dv-sash dv-sash-prime"' in entry or "class='prime-meta'" in entry or 'class="prime-logo"' in entry or "class='item-green'" in entry or 'class="packshot-' in entry)):
            match = re.compile('data-type="(.+?)"', re.DOTALL).findall(entry)
            if not match:
                match = re.compile('type="(.+?)" asin=', re.DOTALL).findall(entry)
            if match:
                if match[0] in ["downloadable_season", "tv", "season"]:
                    videoType = "tv"
                elif match[0] in ["downloadable_movie", "movie"]:
                    videoType = "movie"
                else:
                    print match[0]
                    return
                match = re.compile('" data-asin="(.+?)"', re.DOTALL).findall(entry)
                if not match:
                    match = re.compile('id="(.+?)"', re.DOTALL).findall(entry)
                videoID = match[0]

                match = re.compile('data-title="(.+?)"', re.DOTALL).findall(entry)
                if not match:
                  match = re.compile('<img alt="(.+?)" height', re.DOTALL).findall(entry)
                title = match[0]

                match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
                thumbUrl = ""
                if match:
                    thumbUrl = ScrapeUtils.VideoImage().ImageFile(match[0])
                avail = ''
                if showAvailability:
                    match = re.compile('\<span\s+class\s*=\s*"packshot-message"\s*\>(.+?)\<\/span\>', re.DOTALL).findall(entry)
                    if match:
                        avail=" - " + cleanInput(match[0])

                if videoType == "tv":
                    if useWLSeriesComplete:
                        dlParams.append({'type':videoType, 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'year':''})
                        title = cleanSeasonTitle(title)+avail

                        if title in showEntries:
                            continue

                        addShowDirR(cleanTitleTMDB(title) + avail, videoID, "listSeasons", thumbUrl, videoType, showAll=True)
                        showEntries.append(title)
                    else:
                        title = cleanTitle(title)
                        dlParams.append({'type':videoType, 'id':videoID, 'title':cleanTitleTMDB(cleanTitle(title)), 'year':''})
                        addShowDirR(cleanTitleTMDB(title) + avail, videoID, "listEpisodes", thumbUrl, videoType)

                else: #movie
                    title = cleanTitle(title)
                    dlParams.append({'type':videoType, 'id':videoID, 'title':cleanTitleTMDB(cleanTitle(title)), 'year':''})
                    addLinkR(cleanTitleTMDB(title) + avail, videoID, "playVideo", thumbUrl, videoType)



    match_nextpage = re.compile('<a href=".+?dv_web_wtls_pg_nxt.+?&page=(.+?)&.+?">', re.DOTALL).findall(content)
    if match_nextpage:
        addDir(translation(30001), url + "&page=" + match_nextpage[0].strip(), "listWatchList", "DefaultTVShows.png")
    if videoType == "movie":
        xbmcplugin.setContent(pluginhandle, "movies")
    else:
        xbmcplugin.setContent(pluginhandle, "tvshows")
    if useTMDb and videoType == "movie":
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScript+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    elif useTMDb:
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScriptTV+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        if videoType == "movie":
            xbmc.executebuiltin('Container.SetViewMode('+viewIdMovies+')')
        else:
            xbmc.executebuiltin('Container.SetViewMode('+viewIdShows+')')


def listMovies(url):
    xbmcplugin.setContent(pluginhandle, "movies")
    content = getUnicodePage(url)
    debug('listMovies')
    #debug(url)
    #debug(content)
    content = content.replace("\\","")
    if 'id="catCorResults"' in content:
        content = content[:content.find('id="catCorResults"')]
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])

    args = urlparse.parse_qs(url[1:])
    page = args.get('page', None)
    if page is not None:
        if int(page[0]) > 1:
            content = content[content.find('breadcrumb.breadcrumbSearch'):]

    spl = content.split('id="result_')
    dlParams = []
    videoimage = ScrapeUtils.VideoImage()
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('asin="(.+?)"', re.DOTALL).findall(entry)
        #if match and '>Amazon Video:' in entry:
        if True:
            videoID = match[0]
            match1 = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            match2 = re.compile('class="ilt2">(.+?)<', re.DOTALL).findall(entry)
            title = None
            if match1:
                title = match1[0]
            elif match2:
                title = match2[0]
            title = cleanTitle(title)
            match1 = re.compile('class="a-size-small a-color-secondary">(.+?)<', re.DOTALL).findall(entry)
            match2 = re.compile('class="med reg subt">(.+?)<', re.DOTALL).findall(entry)
            year = ""
            if match1:
                year = match1[0].strip()
            if match2:
                year = match2[0].strip()
            dlParams.append({'type':'movie', 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'year':year})
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            #thumbUrl = match[0].replace(".jpg", "")
            #thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
            thumbUrl = videoimage.ImageFile(match[0])
            match = re.compile('data-action="s-watchlist-add".+?class="a-button a-button-small(.+?)"', re.DOTALL).findall(entry)
            log(videoID, xbmc.LOGDEBUG)
            if match and match[0]==" s-hidden":
                addLinkR(title, videoID, "playVideo", thumbUrl, "movie", "", "", year)
            else:
                addLink(title, videoID, "playVideo", thumbUrl, "movie", "", "", year)
    if useTMDb:
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScript+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    match = re.compile('class="pagnNext".*?href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir(translation(30001), urlMain+match[0].replace("&amp;","&"), "listMovies", "DefaultTVShows.png")
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdMovies+')')


def listShows(url):
    xbmcplugin.setContent(pluginhandle, "tvshows")
    content = getUnicodePage(url)
    debug('listShows')
    #debug(content)
    content = content.replace("\\","")
    if 'id="catCorResults"' in content:
        content = content[:content.find('id="catCorResults"')]
    match = re.compile('"csrfToken":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    spl = content.split('id="result_')
    showEntries = []
    dlParams = []
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('asin="(.+?)"', re.DOTALL).findall(entry)
        isPaidVideo = False
        if showPaidVideos:
            if ">Shop Instant Video<" in entry:
                isPaidVideo = True
            if ">Amazon Video:<" in entry:
                isPaidVideo = True
        #if match and ">Prime Instant Video<" in entry:
        #if match and ((">Prime Video<" in entry) or (isPaidVideo)):
        if True:
            videoID = match[0]
            match1 = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            match2 = re.compile('class="ilt2">(.+?)<', re.DOTALL).findall(entry)
            title = ""
            if match1:
                title = match1[0]
            elif match2:
                title = match2[0]
            title = cleanTitle(title)
            title = cleanSeasonTitle(title)
            if title in showEntries:
                continue
            showEntries.append(title)
            match1 = re.compile('class="a-size-small a-color-secondary">(.+?)<', re.DOTALL).findall(entry)
            match2 = re.compile('class="med reg subt">(.+?)<', re.DOTALL).findall(entry)
            year = ""
            if match1:
                year = match1[0].strip()
            if match2:
                year = match2[0].strip()
            dlParams.append({'type':'tv', 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'year':year})
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumbUrl = match[0].replace(".jpg", "")
            thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
            match = re.compile('data-action="s-watchlist-add".+?class="a-button a-button-small(.*?)"', re.DOTALL).findall(entry)
            if match and match[0]==" s-hidden":
                addShowDirR(title, videoID, "listSeasons", thumbUrl, "tv")
            else:
                addShowDir(title, videoID, "listSeasons", thumbUrl, "tv")
    if useTMDb:
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScriptTV+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    match = re.compile('class="pagnNext".*?href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir(translation(30001), urlMain+match[0].replace("&amp;","&"), "listShows", "DefaultTVShows.png")
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdShows+')')


def listSimilarMovies(videoID):
    xbmcplugin.setContent(pluginhandle, "movies")
    content = getUnicodePage(urlMain+"/gp/product/"+videoID)
    debug('listSimilarMovies')
    #debug(content)
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    spl = content.split('<li class="packshot')
    dlParams = []
    for i in range(1, len(spl), 1):
        entry = spl[i]
        entry = entry[:entry.find('</li>')]
        if 'packshot-sash-prime' in entry:
            match = re.compile("data-type='downloadable_(.+?)'", re.DOTALL).findall(entry)
            if match:
                videoType = match[0]
                match = re.compile("asin='(.+?)'", re.DOTALL).findall(entry)
                videoID = match[0]
                match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
                title = match[0]
                title = cleanTitle(title)
                dlParams.append({'type':'movie', 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'year':''})
                match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
                thumbUrl = ""
                if match:
                    thumbUrl = match[0].replace(".jpg", "")
                    thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
                if videoType == "movie":
                    addLinkR(title, videoID, "playVideo", thumbUrl, videoType)
    if useTMDb:
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScript+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdMovies+')')


def listSimilarShows(videoID):
    xbmcplugin.setContent(pluginhandle, "tvshows")
    content = getUnicodePage(urlMain+"/gp/product/"+videoID)
    debug("listSimilarShows")
    #debug(content)
    match = re.compile("token : '(.+?)'", re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    spl = content.split('<li class="packshot')
    showEntries = []
    dlParams = []
    for i in range(1, len(spl), 1):
        entry = spl[i]
        entry = entry[:entry.find('</li>')]
        if 'packshot-sash-prime' in entry:
            match = re.compile("data-type='downloadable_(.+?)'", re.DOTALL).findall(entry)
            if match:
                videoType = match[0]
                match = re.compile("asin='(.+?)'", re.DOTALL).findall(entry)
                videoID = match[0]
                match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
                title = match[0]
                title = cleanTitle(title)
                dlParams.append({'type':'tv', 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'year':''})
                match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
                thumbUrl = ""
                if match:
                    thumbUrl = match[0].replace(".jpg", "")
                    thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
                if videoType=="tv_season":
                    videoType="tv"
                    title = cleanSeasonTitle(title)
                    if title in showEntries:
                        continue
                    showEntries.append(title)
                    addShowDirR(title, videoID, "listSeasons", thumbUrl, videoType)
    if useTMDb:
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScriptTV+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdShows+')')


def listSeasons(seriesName, seriesID, thumb, showAll = False):
    xbmcplugin.setContent(pluginhandle, "seasons")
    content = getUnicodePage(urlMain+"/gp/product/"+seriesID)
    debug("listSeasons")
    #debug(content)
    match = re.compile('"csrfToken":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    if '<select name="seasonSelector"' in content:
        content = content[content.find('<select name="seasonSelector"'):]
        content = content[:content.find('</select>')]
        match = re.compile('<option value="(.+?):.+?data-a-html-content="(.+?)"', re.DOTALL).findall(content)
        if match:
            for seasonID, title in match:
                if "dv-season-selector-prime" in title or showAll or showPaidVideos:
                    title = title[title.find("&gt;") + 4:]
                    title = title[:title.find("&lt")]
                    addSeasonDir(title, seasonID, 'listEpisodes', thumb, seriesName, seriesID)
            xbmcplugin.endOfDirectory(pluginhandle)
            xbmc.sleep(100)
            if forceView:
                xbmc.executebuiltin('Container.SetViewMode('+viewIdSeasons+')')
    elif '<div class="dv-dropdown-single">' in content:
        content = content[content.find('<div class="dv-dropdown-single">'):]
        content = content[:content.find('<li class="selected-episode')]
        match = re.compile('<div class="dv-dropdown-single">(.+?)<', re.DOTALL).findall(content)
        if match:
            for title in match:
                title = title.strip()
                if "dv-dropdown-prime" in content or showAll or showPaidVideos:
                    addSeasonDir(title, seriesID, 'listEpisodes', thumb, seriesName, seriesID)
            xbmcplugin.endOfDirectory(pluginhandle)
            xbmc.sleep(100)
            if forceView:
                xbmc.executebuiltin('Container.SetViewMode('+viewIdSeasons+')')
    else:
        # listEpisodes(seriesID, seriesID, thumb, contentMain)
        listEpisodes(seriesID, seriesID, thumb)


def listEpisodes(seriesID, seasonID, thumb, content="", seriesName=""):
    xbmcplugin.setContent(pluginhandle, "episodes")
    if not content:
        content = getUnicodePage(urlMain+"/gp/product/"+seasonID)
    debug("listEpisodes:" + urlMain+"/gp/product/"+seasonID)
    #debug(content)
    match = re.compile('"csrfToken":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    matchSeason = re.compile('"seasonNumber":"(.+?)"', re.DOTALL).findall(content)
    seasonNr="0"
    if matchSeason:
        seasonNr=matchSeason[0]

    epliststart = content.find("dv-episode-list")
    eplistend = content.find("ND dv-dp-top-wrapper", epliststart)
    content = content[epliststart:eplistend]
    spl = content.split('<div class="dv-episode-container aok-clearfix" id="dv-el-id-')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<!-- Title -->(.+?)</', re.DOTALL).findall(entry)
        if match and checkEpisodeStatus(entry):
            title = match[0]
            title = cleanTitle(title)
            episodeNr = title[:title.find('.')]
            title = title[title.find('.')+1:].strip()
            match = re.compile('data-asin="(.+?)"', re.DOTALL).findall(entry)
            episodeID = match[0]
            match = re.compile('<p class="a-color-base a-text-normal">(.+?)</p>', re.DOTALL).findall(entry)
            desc = ""
            if match:
                desc = cleanTitle(match[0])
            length = ""
            match1 = re.compile('class="dv-badge runtime">(.+?)h(.+?)min<', re.DOTALL).findall(entry)
            match2 = re.compile('class="dv-badge runtime">(.+?)Std.(.+?)Min.<', re.DOTALL).findall(entry)
            match3 = re.compile('class="dv-badge runtime">(.+?)min<', re.DOTALL).findall(entry)
            match4 = re.compile('class="dv-badge runtime">(.+?)Min.<', re.DOTALL).findall(entry)
            if match1:
                length = str(int(match1[0][0].strip())*60+int(match1[0][1].strip()))
            elif match2:
                length = str(int(match2[0][0].strip())*60+int(match2[0][1].strip()))
            elif match3:
                length = match3[0].strip()
            elif match4:
                length = match4[0].strip()
            match = re.compile('class="dv-badge release-date">(.+?)<', re.DOTALL).findall(entry)
            aired = ""
            if match:
                aired = match[0]+"-01-01"
            match = re.compile('background-image: url\((.+?)\);', re.DOTALL).findall(entry)
            if match:
                thumb = match[0].replace("._SX133_QL80_.jpg","._SX400_.jpg")
            match = re.compile('class="progress-bar">.+?width: (.+?)%', re.DOTALL).findall(entry)
            playcount = 0
            if match:
                percentage = match[0]
                if int(percentage)>95:
                    playcount = 1
            addEpisodeLink(title, episodeID, 'playVideo', thumb, desc, length, seasonNr, episodeNr, seriesID, playcount, aired, seriesName)
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdEpisodes+')')


def listGenres(url, videoType):
    content = getUnicodePage(url)
    #debug(url)
    #debug(content)
    content = content[content.find('<ul class="s-see-all-pagination-column vPage1">'):]
    content = content[:content.find('</div>')]
    match = re.compile('href="(.+?)">.+?>(.+?)</span>.+?>(.+?)<', re.DOTALL).findall(content)
    for url, title, nr in match:
        if videoType=="movie":
            addDir(cleanTitle(title), urlMain+url.replace("/s/","/mn/search/ajax/").replace("&amp;","&"), 'listMovies', "")
        else:
            addDir(cleanTitle(title), urlMain+url.replace("/s/","/mn/search/ajax/").replace("&amp;","&"), 'listShows', "")
    xbmcplugin.endOfDirectory(pluginhandle)

def playVideo(videoID, selectQuality=False, playTrailer=False):
    try:
        #get the player - token
        token = getUnicodePage(urlMainS+'/gp/video/streaming/player-token.json?callback=onWebToken_1')
        token = re.findall('onWebToken_1\({\"token\":\"(.*?)\"}\)', token)[0]
        if not token:
            return None

        #get the CustomerId and build the deviceId
        dealContent = getUnicodePage(urlMainS+'/gp/deal/ajax/getNotifierResources.html')
        dealContent = json.loads(dealContent)
        customerID = dealContent['resourceData']['GBCustomerData']['customerId']
        log('CustomerID: ' + customerID)
        if not customerID:
            return None

        deviceID = hashlib.sha224("CustomerID" + userAgent).hexdigest()

        asinurl = recourceMain+'/cdp/catalog/GetPlaybackResources?asin='+videoID+'&consumptionType=Streaming&desiredResources=AudioVideoUrls%2CCatalogMetadata%2CTransitionTimecodes%2CTrickplayUrls%2CSubtitlePresets%2CSubtitleUrls&deviceID='+deviceID+'&deviceTypeID=AOAGZA014O5RE&firmware=1&marketplaceID='+marketplaceId+'&resourceUsage=CacheResources&videoMaterialType=Feature&operatingSystemName=Windows&operatingSystemVersion=10.0&customerID='+customerID+'&token='+token+'&deviceDrmOverride=CENC&deviceStreamingTechnologyOverride=DASH&deviceProtocolOverride=Https&deviceBitrateAdaptationsOverride=CVBR%2CCBR&audioTrackId=all&titleDecorationScheme=primary-content'
        if platform.platform().find('Android') == -1 :
            asinurl = asinurl + '&supportedDRMKeyScheme=DUAL_KEY'

        asincontent = getUnicodePage(asinurl)
        #debug(asincontent)
        asininfo = json.loads(asincontent)
        mpdURL = asininfo['audioVideoUrls']['avCdnUrlSets'][0]['avUrlInfoList'][0]['url'];
        if not mpdURL:
            return None
        mpdURL = mpdURL.replace("https", "http")
        log('MPD: '+mpdURL)

        mpdURL = re.sub(r'~', '', mpdURL) if mpdURL != re.sub(r'~', '', mpdURL) else re.sub(r'/[1-9][$].*?/', '/', mpdURL)
        log('MPD: '+mpdURL)

        cookies = ";".join(["%s=%s" % (cookie.name, cookie.value) for cookie in cj])
        licURL = recourceMain+'/cdp/catalog/GetPlaybackResources?asin='+videoID+'&consumptionType=Streaming&desiredResources=Widevine2License&deviceID='+deviceID+'&deviceTypeID=AOAGZA014O5RE&firmware=1&marketplaceID='+marketplaceId+'&resourceUsage=ImmediateConsumption&videoMaterialType=Feature&operatingSystemName=Windows&operatingSystemVersion=10.0&customerID='+customerID+'&token='+token+'&deviceDrmOverride=CENC&deviceStreamingTechnologyOverride=DASH|Cookie='+urllib.quote_plus(cookies)+'&Content-Type=application%2Fx-www-form-urlencoded|widevine2Challenge=B{SSM}&includeHdcpTestKeyInLicense=true|JBlicense;hdcpEnforcementResolutionPixels'

        listitem = xbmcgui.ListItem(path=mpdURL)
        listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        listitem.setProperty('inputstream.adaptive.license_key', licURL)
        listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        listitem.setMimeType('application/dash+xml')
        listitem.setContentLookup(False)

        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem=listitem)

    except:
        return False

def showInfo(videoID):
    xbmcplugin.setContent(pluginhandle, "movies")
    content = getUnicodePage(urlMain+"/dp/"+videoID + "/?_encoding=UTF8")
    match=re.compile('property="og:title" content="Watch (.+?) Online - Amazon Video"', re.DOTALL).findall(content)
    title = match[0]
    match=re.compile('class="release-year".*?>(.+?)<', re.DOTALL).findall(content)
    year = match[0]
    title = title+" ("+year+")"
    title = cleanTitle(title)
    match=re.compile('property="og:image" content="(.+?)"', re.DOTALL).findall(content)
    thumb = match[0].replace(".jpg", "")
    thumb = thumb[:thumb.rfind(".")]+".jpg"
    match=re.compile('"director":.+?"name":"(.+?)"', re.DOTALL).findall(content)
    director = match[0].replace(",",", ")
    match=re.compile('"actor":.+?"name":"(.+?)"', re.DOTALL).findall(content)
    actors = match[0].replace(",",", ")
    match=re.compile('property="og:duration" content="(.+?)"', re.DOTALL).findall(content)
    length = str(int(match[0])/60)+" min."
    match=re.compile('property="og:rating" content="(.+?)"', re.DOTALL).findall(content)
    rating = match[0]
    match=re.compile('property="og:rating_count" content="(.+?)"', re.DOTALL).findall(content)
    ratingCount = match[0]
    match=re.compile('property="og:description" content="(.+?)"', re.DOTALL).findall(content)
    description = cleanTitle(match[0])
    match=re.compile('"genre":"(.+?)"', re.DOTALL).findall(content)
    genre = u""
    if match:
        genre = match[0]
    addLink(title, videoID, "playVideo", thumb, videoType="movie", desc=description, duration=length, year=year, mpaa="", director=director, genre=genre, rating=rating)
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdDetails+')')
    try:
        wnd = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        wnd.getControl(wnd.getFocusId()).selectItem(1)
    except:
        pass


def deleteCookies():
    if os.path.exists(cookieFile):
        os.remove(cookieFile)


def deleteCache():
    if os.path.exists(cacheFolder):
        try:
            shutil.rmtree(cacheFolder)
        except:
            shutil.rmtree(cacheFolder)

def getUnicodePage(url):
    print url
    req = opener.open(url)

    if req.info().get('Content-Encoding') == 'gzip':
        content = StringIO( req.read())
        f = gzip.GzipFile(fileobj=content)
        content = f.read()
    else :
        content = req.read()

    if "content-type" in req.headers and "charset=" in req.headers['content-type']:
        encoding=req.headers['content-type'].split('charset=')[-1]
        content = unicode(content, encoding)
    else:
        content = unicode(content, "utf-8")
    return content

def getAsciiPage(url):
    req = opener.open(url)
    content = req.read()
    if "content-type" in req.headers and "charset=" in req.headers['content-type']:
        encoding=req.headers['content-type'].split('charset=')[-1]
        content = unicode(content, encoding)
    else:
        content = unicode(content, "utf-8")
    return content.encode("utf-8")

def cipherKey(s, key="xlordkx"):
    key = unicode(key).encode("utf-8")
    keyarr = map(ord, key)
    key = b""
    for i in range(len(keyarr)):
        key += str(keyarr[i])
    s = base64.b64decode(s)
    random.seed(long(key))
    bytearr = map (ord, s )
    o = b""
    for i in range(len(bytearr)):
        o += (chr(bytearr[i] ^ random.randint(0, 255)))
    return unicode(o)

def search(type):
    keyboard = xbmc.Keyboard('', translation(30015))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = unicode(keyboard.getText(), "utf-8").replace(" ", "+")
        search_string = urllib.quote_plus(search_string.encode("utf8"))
        if siteVersion=="de":
            if type=="movies":
                listMovies(urlMain+"/mn/search/ajax/?fst=as%3Aoff&rh=n%3A3010075031%2Cn%3A!3010076031%2Cn%3A3015915031%2Ck%3A"+search_string+"%2Cp_85%3A3282148031")
            elif type=="tv":
                listShows(urlMain+"/mn/search/ajax/?fst=as%3Aoff&rh=n%3A3010075031%2Cn%3A!3010076031%2Cn%3A3015916031%2Ck%3A"+search_string+"%2Cp_85%3A3282148031&qid=1453585050")
        elif siteVersion=="com":
            if type=="movies":
                listMovies(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D7613704011&search-alias=instant-video&field-keywords="+search_string)
            elif type=="tv":
                if not showPaidVideos:
                    listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D7613705011&search-alias=instant-video&field-keywords="+search_string)
                else:
                    listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D2858778011&search-alias=instant-video&field-keywords="+search_string)
        elif siteVersion=="co.uk":
            if type=="movies":
                listMovies(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3356010031&search-alias=instant-video&field-keywords="+search_string)
            elif type=="tv":
                listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3356011031&search-alias=instant-video&field-keywords="+search_string)
        elif siteVersion=="co.jp":
            if type=="movies":
                listMovies(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D33535604051&search-alias=instant-video&field-keywords="+search_string)
            elif type=="tv":
                listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3535604051&search-alias=instant-video&field-keywords="+search_string)



def addToQueue(videoID, videoType):
    if videoType=="tv":
        videoType = "tv_episode"
    content = getUnicodePage(urlMain+"/gp/video/watchlist/ajax/addRemove.html/ref=sr_1_1_watchlist_add?token="+urllib.quote_plus(addon.getSetting('csrfToken').encode("utf8"))+"&dataType=json&prodType="+videoType+"&ASIN="+videoID+"&pageType=Search&subPageType=SASLeafSingleSearch&store=instant-video")
    if showNotification:
        xbmc.executebuiltin(unicode('XBMC.Notification(Info:,'+translation(30088)+',3000,'+icon+')').encode("utf-8"))


def removeFromQueue(videoID, videoType):
    if videoType=="tv":
        videoType = "tv_episode"
    content = getUnicodePage(urlMain+"/gp/video/watchlist/ajax/addRemove.html/ref=sr_1_1_watchlist_remove?token="+urllib.quote_plus(addon.getSetting('csrfToken').encode("utf8"))+"&dataType=json&prodType="+videoType+"&ASIN="+videoID+"&pageType=Search&subPageType=SASLeafSingleSearch&store=instant-video")
    xbmc.executebuiltin("Container.Refresh")
    if showNotification:
        xbmc.executebuiltin(unicode('XBMC.Notification(Info:,'+translation(30089)+',3000,'+icon+')').encode("utf-8"))


def login(content = None, statusOnly = False):
    if content is None:
        content = getUnicodePage(urlMainS)
    signoutmatch = re.compile("declare\('config.signOutText',(.+?)\);", re.DOTALL).findall(content)
    if '","isPrime":1' in content: #
        return "prime"
    elif signoutmatch[0].strip() != "null":
        return "noprime"
    else:
        if statusOnly:
            return "none"

        deleteCookies()
        content = ""
        keyboard = xbmc.Keyboard('', translation(30090))
        keyboard.doModal()
        if keyboard.isConfirmed() and unicode(keyboard.getText(), "utf-8"):
            email = unicode(keyboard.getText(), "utf-8")
            keyboard = xbmc.Keyboard('', translation(30091), True)
            keyboard.setHiddenInput(True)
            keyboard.doModal()
            if keyboard.isConfirmed() and unicode(keyboard.getText(), "utf-8"):
                password = unicode(keyboard.getText(), "utf-8")
                br = mechanize.Browser()
                br.set_cookiejar(cj)
                br.set_handle_robots(False)
                br.set_handle_gzip(True)
                br.addheaders = [('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
                                ('Accept-Language', 'de,en-US;q=0.8,en;q=0.6'),
                                ('Cache-Control', 'max-age=0'),
                                ('Connection', 'keep-alive'),
                                ('Content-Type', 'application/x-www-form-urlencoded'),
                                ('User-Agent', userAgent),
                                ('Upgrade-Insecure-Requests', '1')]
                content = br.open(urlMainS+"/gp/sign-in.html")
                br.select_form(name="signIn")
                br["email"] = email
                br["password"] = password
                content = br.submit().read()
                cj.save(cookieFile)
                cj.load(cookieFile)
                content = getUnicodePage(urlMainS)
        signoutmatch = re.compile("declare\('config.signOutText',(.+?)\);", re.DOTALL).findall(content)
        if '","isPrime":1' in content: #
            return "prime"
        elif signoutmatch[0].strip() != "null":
            return "noprime"
        else:
            return "none"

def safeint(x):
   base=10 if x.find("x")==-1 else 16
   return int(x.replace("x",""),base)

def cleanInput(str):
    if type(str) is not unicode:
        str = unicode(str, "iso-8859-15")
        xmlc = re.compile('&#(.+?);', re.DOTALL).findall(str)
        for c in xmlc:
            str = str.replace("&#"+c+";", unichr(safeint(c)))

    p = HTMLParser()
    str = p.unescape(str)
    return str

def cleanTitle(title):
    if "[HD]" in title:
        title = title[:title.find("[HD]")]
    return cleanInput(title)


def cleanSeasonTitle(title):
    if ": The Complete" in title:
        title = title[:title.rfind(": The Complete")]
    if ": Season" in title:
        title = title[:title.rfind(": Season")]
    if "Season" in title:
        title = title[:title.rfind("Season")]
    if "Staffel" in title:
        title = title[:title.rfind("Staffel")]
    if "Volume" in title:
        title = title[:title.rfind("Volume")]
    if "Series" in title:
        title = title[:title.rfind("Series")]
    title = title.strip(" -,")

    xmlc = re.compile('&#(.+?);', re.DOTALL).findall(title)
    for c in xmlc:
        title = title.replace("&#"+c+";", unichr(safeint(c)))

    return title

def cleanTitleTMDB(title):
    if "[" in title:
        title = title[:title.find("[")]
    if " OmU" in title:
        title = title[:title.find(" OmU")]
    return title


def addMovieToLibrary(movieID, title):
    #title = title.decode('iso-8859-1').encode('iso-8859-1')
    movieFolderName = (''.join(c for c in title if c not in '/\\:?"*|<>')).strip(' .')
    dir = os.path.join(libraryFolderMovies, movieFolderName)
    if not os.path.exists(dir):
        xbmcvfs.mkdir(unicode(dir).encode("iso-8859-1"))
        fh = xbmcvfs.File(unicode(os.path.join(dir, "movie.strm")).encode("iso-8859-1"), 'w')
        fh.write(unicode('plugin://'+addonID+'/?mode=playVideo&url='+movieID).encode("utf-8"))
        fh.close()
    if updateDB:
        xbmc.executebuiltin(unicode('UpdateLibrary(video)').encode("utf-8"))


def addSeasonToLibrary(seriesID, seriesTitle, seasonID):
    seriesFolderName = (''.join(c for c in seriesTitle if c not in '/\\:?"*|<>')).strip(' .')
    seriesDir = os.path.join(libraryFolderTV, seriesFolderName)
    if not os.path.isdir(seriesDir):
        xbmcvfs.mkdir(unicode(seriesDir).encode("iso-8859-1"))
    content = getUnicodePage(urlMain+"/gp/product/"+seasonID)
    matchSeason = re.compile('"seasonNumber":"(.+?)"', re.DOTALL).findall(content)
    spl = content.split('href="'+urlMain+'/gp/product')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('class="episode-title">(.+?)<', re.DOTALL).findall(entry)
        if match:
            title = match[0]
            title = cleanTitle(title)
            episodeNr = title[:title.find('.')]
            title = title[title.find('.')+1:].strip()
            match = re.compile('/(.+?)/', re.DOTALL).findall(entry)
            episodeID = match[0]
            if len(episodeNr) > 2:
                episodeNr = ''.join(re.findall(r'\d+', episodeNr))
            if len(episodeNr) == 1:
                episodeNr = "0"+episodeNr
            seasonNr = matchSeason[0]
            if len(seasonNr) == 1:
                seasonNr = "0"+seasonNr
            filename = "S"+seasonNr+"E"+episodeNr+" - "+title+".strm"
            filename = (''.join(c for c in filename if c not in '/\\:?"*|<>')).strip(' .')
            print type(filename)
            fh = xbmcvfs.File(unicode(os.path.join(seriesDir, filename)).encode('utf-8'), 'w')
            fh.write(unicode('plugin://'+addonID+'/?mode=playVideo&url='+episodeID).encode("utf-8"))
            fh.close()
    if updateDB:
        xbmc.executebuiltin('UpdateLibrary(video)')


def debug(content):
    if (NODEBUG):
        return
    #print unicode(content).encode("utf-8")
    #log(content, xbmc.LOGDEBUG)
    log(unicode(content), xbmc.LOGDEBUG)

def log(msg, level=xbmc.LOGNOTICE):
    # xbmc.log('%s: %s' % (addonID, msg), level)
    log_message = u'{0}: {1}'.format(addonID, msg)
    xbmc.log(log_message.encode("utf-8"), level)
    """
    xbmc.LOGDEBUG = 0
    xbmc.LOGERROR = 4
    xbmc.LOGFATAL = 6
    xbmc.LOGINFO = 1
    xbmc.LOGNONE = 7
    xbmc.LOGNOTICE = 2
    xbmc.LOGSEVERE = 5
    xbmc.LOGWARNING = 3
    """

def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addDir(name, url, mode, iconimage, videoType=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))+"&videoType="+urllib.quote_plus(videoType.encode("utf8"))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "mediatype": videoType})
    liz.setArt({"fanart": defaultFanart, "poster": iconimage})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating="", showAll = False):
    filename = (''.join(c for c in url if c not in '/\\:?"*|<>')).strip()+".jpg"
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    if os.path.exists(coverFile):
        iconimage = coverFile
    sAll = ""
    if (showAll):
        sAll = "&showAll=true"
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))+"&name="+urllib.quote_plus(name.encode("utf8"))+sAll
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setArt({"fanart": fanartFile, "poster": iconimage})
    entries = []
    entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30052), 'RunPlugin(plugin://'+addonID+'/?mode=addToQueue&url='+urllib.quote_plus(url.encode("utf8"))+'&videoType='+urllib.quote_plus(videoType.encode("utf8"))+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDirR(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating="", showAll=False):
    filename = (''.join(c for c in url if c not in '/\\:?"*|<>')).strip()+".jpg"
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    if os.path.exists(coverFile):
        iconimage = coverFile
    sAll = ""
    if showAll:
        sAll = "&showAll=true"
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))+"&name="+urllib.quote_plus(name.encode("utf8"))+sAll
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"mediatype": "tvshow", "title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setArt({"fanart": fanartFile, "poster": iconimage})
    entries = []
    entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30053), 'RunPlugin(plugin://'+addonID+'/?mode=removeFromQueue&url='+urllib.quote_plus(url.encode("utf8"))+'&videoType='+urllib.quote_plus(videoType.encode("utf8"))+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addLink(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating=""):
    filename = (''.join(c for c in url if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&name="+urllib.quote_plus(name.encode("utf8"))+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"mediatype": videoType, "title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setArt({"fanart": fanartFile, "poster": iconimage})
    entries = []
    entries.append((translation(30054), 'RunPlugin(plugin://'+addonID+'/?mode=playVideo&url='+urllib.quote_plus(url.encode("utf8"))+'&selectQuality=true)',))
    #entries.append(("PreCache Video", 'RunPlugin(plugin://'+addonID+'/?mode=precacheVideo&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    if videoType != "episode":
        entries.append((translation(30060), 'Container.Update(plugin://'+addonID+'/?mode=showInfo&url='+urllib.quote_plus(url.encode("utf8"))+')',))
        entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url.encode("utf8"))+')',))
        entries.append((translation(30052), 'RunPlugin(plugin://'+addonID+'/?mode=addToQueue&url='+urllib.quote_plus(url.encode("utf8"))+'&videoType='+urllib.quote_plus(videoType.encode("utf8"))+')',))
    if videoType == "movie":
        titleTemp = name.strip()
        if year:
            titleTemp += ' ('+year+')'
        entries.append((translation(30055), 'RunPlugin(plugin://'+addonID+'/?mode=addMovieToLibrary&url='+urllib.quote_plus(url.encode("utf8"))+'&name='+urllib.quote_plus(titleTemp.encode("utf8"))+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    liz.addContextMenuItems(entries)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addLinkR(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating=""):
    filename = (''.join(c for c in url if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&name="+urllib.quote_plus(name.encode("utf8"))+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"mediatype": videoType, "title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setArt({"fanart": fanartFile, "poster": iconimage})
    entries = []
    entries.append((translation(30054), 'RunPlugin(plugin://'+addonID+'/?mode=playVideo&url='+urllib.quote_plus(url.encode("utf8"))+'&selectQuality=true)',))
    entries.append((translation(30060), 'Container.Update(plugin://'+addonID+'/?mode=showInfo&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30053), 'RunPlugin(plugin://'+addonID+'/?mode=removeFromQueue&url='+urllib.quote_plus(url.encode("utf8"))+'&videoType='+urllib.quote_plus(videoType.encode("utf8"))+')',))
    if videoType == "movie":
        titleTemp = name.strip()
        if year:
            titleTemp += ' ('+year+')'
        entries.append((translation(30055), 'RunPlugin(plugin://'+addonID+'/?mode=addMovieToLibrary&url='+urllib.quote_plus(url.encode("utf8"))+'&name='+urllib.quote_plus(titleTemp.encode("utf8"))+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    liz.addContextMenuItems(entries)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addSeasonDir(name, url, mode, iconimage, seriesName, seriesID):
    filename = (''.join(c for c in seriesID if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&seriesID="+urllib.quote_plus(seriesID.encode("utf8"))+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))+"&name="+urllib.quote_plus(seriesName.encode("utf8"))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "TVShowTitle": seriesName, "mediatype": "season"})
    liz.setArt({"fanart": fanartFile, "poster": iconimage})
    entries = []
    entries.append((translation(30056), 'RunPlugin(plugin://'+addonID+'/?mode=addSeasonToLibrary&url='+urllib.quote_plus(url.encode("utf8"))+'&seriesID='+urllib.quote_plus(seriesID.encode("utf8"))+'&name='+urllib.quote_plus(seriesName.strip().encode("utf8"))+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addEpisodeLink(name, url, mode, iconimage, desc="", duration="", season="", episodeNr="", seriesID="", playcount="", aired="", seriesName=""):
    filename = (''.join(c for c in seriesID if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "mediatype": "episode", "plot": desc, "duration": duration, "season": season, "episode": episodeNr, "aired": aired, "playcount": playcount, "TVShowTitle": seriesName})
    liz.setArt({"fanart": fanartFile})
    entries = []
    entries.append((translation(30054), 'RunPlugin(plugin://'+addonID+'/?mode=playVideo&url='+urllib.quote_plus(url.encode("utf8"))+'&selectQuality=true)',))
    liz.addContextMenuItems(entries)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def checkEpisodeStatus(entry):
    return '?autoplay=1' in entry

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
name = urllib.unquote_plus(params.get('name', ''))
season = urllib.unquote_plus(params.get('season', ''))
showAllSeasons = urllib.unquote_plus(params.get('showAll', '')) == "true"
seriesID = urllib.unquote_plus(params.get('seriesID', ''))
videoType = urllib.unquote_plus(params.get('videoType', ''))
selectQuality = urllib.unquote_plus(params.get('selectQuality', ''))

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not os.path.isdir(cacheFolder):
    os.mkdir(cacheFolder)
if not os.path.isdir(cacheFolderCoversTMDB):
    os.mkdir(cacheFolderCoversTMDB)
if not os.path.isdir(cacheFolderFanartTMDB):
    os.mkdir(cacheFolderFanartTMDB)
if not os.path.isdir(libraryFolder):
    os.mkdir(libraryFolder)
if not os.path.isdir(libraryFolderMovies):
    os.mkdir(libraryFolderMovies)
if not os.path.isdir(libraryFolderTV):
    os.mkdir(libraryFolderTV)

if os.path.exists(os.path.join(addonUserDataFolder, "cookies")):
    os.rename(os.path.join(addonUserDataFolder, "cookies"), cookieFile)



if os.path.exists(cookieFile):
    cj.load(cookieFile)
else:
    login()

if mode == 'listMovies':
    listMovies(url)
elif mode == 'listShows':
    listShows(url)
elif mode == 'listWatchList':
    listWatchList(url)
elif mode == 'listGenres':
    listGenres(url, videoType)
elif mode == 'addToQueue':
    addToQueue(url, videoType)
elif mode == 'removeFromQueue':
    removeFromQueue(url, videoType)
elif mode == 'playVideo':
    playVideo(url, selectQuality=="true")
elif mode == 'playVideoSelect':
    playVideo(url, True)
elif mode == 'browseMovies':
    browseMovies()
elif mode == 'browseTV':
    browseTV()
elif mode == 'search':
    search(url)
elif mode == 'login':
    login()
elif mode == 'listDecadesMovie':
    listDecadesMovie()
elif mode == 'listOriginals':
    listOriginals()
elif mode == 'listSeasons':
    listSeasons(name, url, thumb, showAll=showAllSeasons)
elif mode == 'listEpisodes':
    listEpisodes(seriesID, url, thumb, "", name)
elif mode == 'deleteCookies':
    deleteCookies()
elif mode == 'deleteCache':
    deleteCache()
elif mode == 'playTrailer':
    playVideo(url, selectQuality=="true", True)
elif mode == 'listSimilarMovies':
    listSimilarMovies(url)
elif mode == 'listSimilarShows':
    listSimilarShows(url)
elif mode == 'showInfo':
    showInfo(url)
elif mode == 'addMyListToLibrary':
    addMyListToLibrary()
elif mode == 'addMovieToLibrary':
    addMovieToLibrary(url, name)
elif mode == 'addSeasonToLibrary':
    addSeasonToLibrary(seriesID, name, url)
else:
    index()
