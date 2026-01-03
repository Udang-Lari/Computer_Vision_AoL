const playlist = [
    { 
        title: "BIRDS OF A FEATHER", 
        artist: "Billie Eilish", 
        file: "/static/music/BIRDS OF A FEATHER.mp3", 
        cover: "https://i.scdn.co/image/ab67616d0000b27371d62ea7ea8a5be92d3c1f62" 
    },
    { 
        title: "Best Friend", 
        artist: "Rex Orange County", 
        file: "/static/music/Best Friend.mp3", 
        cover: "https://i.scdn.co/image/ab67616d0000b273ff874602e13e9181c26e5f01" 
    },
    { 
        title: "Dan...", 
        artist: "Sheila On 7", 
        file: "/static/music/Dan....mp3", 
        cover: "https://i.scdn.co/image/ab67616d0000b27354270208627aa8061a8abe21" 
    },
    { 
        title: "Espresso", 
        artist: "Sabrina Carpenter", 
        file: "/static/music/Espresso.mp3", 
        cover: "https://i.scdn.co/image/ab67616d0000b273659cd4673230913b3918e0d5" 
    },
    { 
        title: "Kasih Aba Aba", 
        artist: "Naykilla, Tenxi, Jemsii", 
        file: "/static/music/Kasih Aba Aba.mp3", 
        cover: "https://i.scdn.co/image/ab67616d0000b2738afa25403ff8a518ee7a9f94" 
    },
    { 
        title: "Kill Bill", 
        artist: "SZA", 
        file: "/static/music/Kill Bill.mp3", 
        cover: "https://i.scdn.co/image/ab67616d0000b273c5276ed6cb0287df8d9be07f" 
    },
    { 
        title: "Sialan", 
        artist: "Juicy Luicy", 
        file: "/static/music/Sialan.mp3", 
        cover: "https://i.scdn.co/image/ab67616d0000b273c1b41bef62365566a42821bd" 
    },
    { 
        title: "Sofia", 
        artist: "Clairo", 
        file: "/static/music/Sofia.mp3", 
        cover: "https://i.scdn.co/image/ab67616d0000b27333ccb60f9b2785ef691b2fbc" 
    },
    { 
        title: "TABOLA BALE", 
        artist: "Silet Open Up", 
        file: "/static/music/TABOLA BALE.mp3", 
        cover: "https://i.scdn.co/image/ab67616d00001e0210df7b8e9b3ed2588888a8ae" 
    },
    { 
        title: "You'll Be in My Heart", 
        artist: "Niki", 
        file: "/static/music/You'll Be in My Heart (Spotify Singles).mp3", 
        cover: "https://i.scdn.co/image/ab67616d0000b2737cd329ea4a204a8a47caf3d5" 
    }
];

let currentIdx = 0;
let isPlaying = false;
let lastCommand = "NONE"; 

const audio = document.getElementById('audio-player');
const title = document.getElementById('song-title');
const artist = document.getElementById('song-artist');
const playBtnIcon = document.querySelector('#btn-play i');
const volBar = document.getElementById('ui-vol-bar');
const progressBar = document.getElementById('progress-bar');
const gestureText = document.getElementById('gesture-text');
const albumArt = document.getElementById('cover-img');

function loadSong(idx) {
    title.innerText = playlist[idx].title;
    artist.innerText = playlist[idx].artist;
    audio.src = playlist[idx].file;
    
    if (playlist[idx].cover && playlist[idx].cover !== "") {
        albumArt.src = playlist[idx].cover;
    } else {
        albumArt.src = "https://via.placeholder.com/600/10b981/000000?text=NO+IMAGE";
    }
    
    audio.load();
}

function togglePlay() {
    if (audio.paused) {
        audio.play().then(() => {
            isPlaying = true;
            playBtnIcon.classList.replace('fa-play', 'fa-pause');
            playBtnIcon.classList.remove('pl-2');
        }).catch(e => {
            console.log(e);
            gestureText.innerText = "CLICK TO START";
        });
    } else {
        audio.pause();
        isPlaying = false;
        playBtnIcon.classList.replace('fa-pause', 'fa-play');
        playBtnIcon.classList.add('pl-2');
    }
}

function nextSong() {
    currentIdx = (currentIdx + 1) % playlist.length;
    loadSong(currentIdx);
    if(isPlaying) audio.play();
}

function prevSong() {
    currentIdx = (currentIdx - 1 + playlist.length) % playlist.length;
    loadSong(currentIdx);
    if(isPlaying) audio.play();
}

function startSystem() {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    
    audio.play().then(() => {
        audio.pause();
    }).catch(e => console.log(e));

    const overlay = document.getElementById('start-overlay');
    overlay.style.opacity = '0';
    setTimeout(() => {
        overlay.remove();
    }, 500);
}

loadSong(0);

audio.addEventListener('timeupdate', () => {
    if(audio.duration) {
        const percent = (audio.currentTime / audio.duration) * 100;
        progressBar.style.width = percent + "%";
    }
});

audio.addEventListener('ended', nextSong);

setInterval(() => {
    fetch('/get_state')
        .then(response => response.json())
        .then(data => {
            gestureText.innerText = data.gesture;
            
            if(data.gesture.includes("VOL")) gestureText.className = "text-3xl font-black tracking-widest text-yellow-400 drop-shadow-lg";
            else if(data.gesture.includes("MUTE")) gestureText.className = "text-3xl font-black tracking-widest text-red-500 drop-shadow-lg";
            else if(data.gesture.includes("CMD")) gestureText.className = "text-3xl font-black tracking-widest text-green-500 drop-shadow-lg scale-110 transition";
            else gestureText.className = "text-3xl font-black tracking-widest text-white drop-shadow-lg";

            const targetVol = data.volume / 100;
            if (Math.abs(audio.volume - targetVol) > 0.02) {
                audio.volume = targetVol;
            }
            volBar.style.height = data.volume + "%";

            if (data.command !== "NONE" && data.command !== lastCommand) {
                console.log(data.command);
                
                if (data.command === "NEXT") nextSong();
                else if (data.command === "PREV") prevSong();
                else if (data.command === "PLAY") { if(audio.paused) togglePlay(); }
                else if (data.command === "PAUSE") { if(!audio.paused) togglePlay(); }
                
                lastCommand = data.command;
                setTimeout(() => { lastCommand = "NONE"; }, 1000);
            }
        })
        .catch(err => console.error(err));
}, 100);