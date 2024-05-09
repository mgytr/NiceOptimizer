var changes = {}
const encforHTML = (s) => {return s.replace(/[\u00A0-\u9999<>\&]/g, function(i) {
    return '&#'+i.charCodeAt(0)+';';
 });};
var statuses = {}
eel;


async function requestStatus(check) {
    return await eel.getStatus(check)();
}
const explorerRestartRequired = []
const logoutRequired = ['disableAnimations']
const restartRequired = ['disFstp', 'disThrottling', 'disableDefender', 'disTelemetry', 'disSysRestore']
async function onload() {
    // iterate over all elems with id tab
    let tid = 0
    for (let tab of document.querySelectorAll('div.tabs button')) {
        tid = parseInt(tab.getAttribute('tab'))
        console.log(tab.getAttribute('tab'))
        tab.addEventListener('click', function () {
            if (document.querySelector('button[tab].active') !== null) {
                document.querySelector('button[tab].active').classList.remove('active')

            }
            for (const t of document.querySelectorAll('div.tabcontents div.c')) {
                if ('hidden' in t.classList) {}
                else {t.classList.add('hidden')}
            }  
            tab.classList.add('active')

            document.querySelector(`div.tabcontents div.c[tab="${tab.getAttribute('tab')}"]`).classList.remove('hidden')
            
        })
    }

    for (let cont of document.querySelectorAll('div.tabcontents div.c')) {

        cont.classList.add('hidden');
    }
    document.querySelector('div.tabs button[tab="0"]').click()
    let chid = ''


    for (let chk of document.querySelectorAll('chk')) {

        chid = chk.getAttribute('c')
        setTimeout(async function (chid, chk) {
        statuses[chid] = await requestStatus(chid)
        // set tip in html using title attribute

        chk.outerHTML = `<input title="${chk.getAttribute('t')}" onclick="checkedBox('${chid}')" type="checkbox" ${(statuses[chid] ? 'checked="checked"' : '') } c="${chid}" id="chkbox_${chid}"><label for="chkbox_${chk.getAttribute('c')}">${chk.innerHTML}</label><br>`
        }, 1, chid, chk)
    }


}
let needRestart = []
let needLogout = []
let needExplorerRestart = []


function checkedBox(chid) {

    let elem = document.querySelector(`input[c="${chid}"]`)
    let checked = elem.checked
    let status = statuses[chid]
    let dontcontinue = false
    if (checked == status) {

        delete changes[chid];
        needRestart = needRestart.filter(e => e !== chid)
        needLogout = needLogout.filter(e => e !== chid)
        needExplorerRestart = needExplorerRestart.filter(e => e !== chid)
        document.getElementById('requiredmsg').innerHTML = ''
        
        document.getElementById('latertweaks').className = 'btnn hidden'

        console.log('efjhkljkl')
        dontcontinue = true
        let rmsg = document.getElementById('requiredmsg')
        if (needExplorerRestart.length !== 0) {
            rmsg.innerHTML = 'Explorer restart required'
            document.getElementById('latertweaks').className = 'btnn'
        }
        if (needLogout.length !== 0) {
            rmsg.innerHTML = 'Re log-in required!'
            document.getElementById('latertweaks').className = 'btnn'
        }
    
        if (needRestart.length !== 0) {
            rmsg.innerHTML = 'Restart required!'
            document.getElementById('latertweaks').className = 'btnn'
        }





    }
    else {
        changes[chid] = checked;
    }

    let confirmdiv = document.querySelector('div.confirm')
    // check if any tweaks need restart using 
    if (Object.keys(changes).length === 0 && !confirmdiv.classList.contains('hidden')) {

        document.getElementById('requiredmsg').innerHTML = ''

        let confirmdiv = document.querySelector('div.confirm')
        let laterbtn = document.getElementById('latertweaks')

        laterbtn.classList.add('hidden')


        confirmdiv.className = 'confirm hidden'

    
        changes = {}
        needRestart = []
        needLogout = []
        needExplorerRestart = []

        return    
        
    }
    if (dontcontinue) {return}
    else if (Object.keys(changes).length !== 0 && confirmdiv.classList.contains('hidden')) {
        confirmdiv.classList.remove('hidden')
        
    }
    if (restartRequired.includes(chid)) {
        needRestart.push(chid)
    }
    else if (logoutRequired.includes(chid)) {
        needLogout.push(chid)
    }
    else if (explorerRestartRequired.includes(chid)) {
        needExplorerRestart.push(chid)
    }
    let rmsg = document.getElementById('requiredmsg')
    if (needExplorerRestart.length !== 0) {
        rmsg.innerHTML = 'Explorer restart required'
    }
    if (needLogout.length !== 0) {
        rmsg.innerHTML = 'Re log-in required!'
    }

    if (needRestart.length !== 0) {
        rmsg.innerHTML = 'Restart required!'
    }
    let laterbtn = document.getElementById('latertweaks')
    if (rmsg.innerHTML !== '') {
        try {laterbtn.classList.remove('hidden')}
        catch (e) {}
    }
    else {
        if (!laterbtn.classList.contains('hidden')) {laterbtn.classList.add('hidden')}
    }




}
function discardTweaks() {
    for (const chid of Object.keys(changes)) {
        let elem = document.querySelector(`input[c="${chid}"]`)

        elem.click();
    }
    document.getElementById('requiredmsg').innerHTML = ''
    let confirmdiv = document.querySelector('div.confirm')
    let laterbtn = document.getElementById('latertweaks')
    if (!laterbtn.classList.contains('hidden')) {
        laterbtn.classList.add('hidden')
    }
    if (!confirmdiv.classList.contains('hidden')) {
        confirmdiv.classList.add('hidden')
    }

    changes = {}
    needRestart = []
    needLogout = []
    needExplorerRestart = []




}
function applyTweaks() {
    eel.applyTweaks(changes);
    let restartNeeded = needRestart.length !== 0
    let logoutNeeded = needLogout.length !== 0
    let explorerRestartRequired = needExplorerRestart.length !== 0
    for (const chid of Object.keys(changes)) {
        statuses[chid] = changes[chid]

    }
    
    document.querySelector('div.confirm').classList.add('hidden')
    if (restartNeeded) {
        eel.restart()()
        return
    }
    if (logoutNeeded) {
        eel.logout()()
        return
    }
    if (explorerRestartRequired) {
        eel.explorerRestart()()
        return
    }
    
}