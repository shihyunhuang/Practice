const player = document.querySelector('.player');
const video = player.querySelector('.viewer');
const toggle = player.querySelector('.toggle');
const volumerange = player.querySelector('.volume__slider');
const speedrange = player.querySelector('.speed__slider');
const volumeDisplay = document.getElementById("volumeDisplay");
const speedDisplay = document.getElementById("speedDisplay");
const progressBar = player.querySelectorAll(".progressBar");
const startPointer = document.getElementById("startPointer");
const endPointer = document.getElementById("endPointer");
const progressContainer = document.querySelector(".progress-container");
const countdownbutton = document.getElementById("countdown_turn");
const displaybutton = document.getElementById("display_bone");
const without_pose_video = document.getElementById("without_bone");
const with_pose_video = document.getElementById("with_bone");

with_pose_video.volume = 0;
let isDraggingStart = false;
let isDraggingEnd = false;

function updateButton() {
	const icon = this.paused ? '►' : '❚❚';
	toggle.textContent = icon;
}

without_pose_video.addEventListener('play', updateButton);
without_pose_video.addEventListener('pause', updateButton);
with_pose_video.addEventListener('play', updateButton);
with_pose_video.addEventListener('pause', updateButton);

// 音量、播放速度
function handlespeedRangeUpdate(video, speedDisplay) {
    video[this.name] = this.value;
    speedDisplay.textContent = `播放速度: ${video.playbackRate}`;
}

speedrange.addEventListener('input', function () {
    // Update for without_pose_video
    handlespeedRangeUpdate.call(this, without_pose_video, speedDisplay);
        
    // Update for with_pose_video
    handlespeedRangeUpdate.call(this, with_pose_video, speedDisplay);
});

// 音量、播放速度
function handlevolumeRangeUpdate(video, volumeDisplay) {
    video[this.name] = this.value;
    volumeDisplay.textContent = `音量: ${video.volume}`;
}

volumerange.addEventListener('input', function () {
    // Update for without_pose_video
    handlevolumeRangeUpdate.call(this, without_pose_video, volumeDisplay, speedDisplay);
});


// 初始化进度条
function initProgressBar() {
    const elem = document.getElementById("myBar");
    
    function updateProgressBar() {
        const percent = (video.currentTime) / (video.duration) * 100;
        elem.style.width = `${percent}%`;
        requestAnimationFrame(updateProgressBar);
    }

    // 启动更新进度条的函数
    requestAnimationFrame(updateProgressBar);
}
    
video.addEventListener('timeupdate', initProgressBar);

//指標位置定位
function updatePointerPosition(pointer, event) {
    const rect = progressContainer.getBoundingClientRect();
    const offsetX = event.clientX - rect.left;
    const percent = (offsetX / progressContainer.offsetWidth) * 100;

    if (percent >= 0 && percent <= 100) {
        const labelPercentages = [];
        // 將bpmPercentData中每個percent 属性的值添加到数组中
        for (var i = 0; i < bpmPercentData.length; i++) {
            labelPercentages.push(bpmPercentData[i].left);
        }
        const nearestLabel = labelPercentages.reduce((prev, curr) => {
            return Math.abs(curr - percent) < Math.abs(prev - percent) ? curr : prev;
        });

        pointer.style.left = `${nearestLabel}%`;
    }
}

//偵測滑鼠是否有移動指標
function handlePointerDragStart(event, pointer) {
    event.preventDefault();
    isDraggingStart = false;
    isDraggingEnd = false;
    
    if (pointer === startPointer) {
        isDraggingStart = true;
    } else if (pointer === endPointer) {
        isDraggingEnd = true;
    }

    if (isDraggingStart || isDraggingEnd) {
        document.addEventListener("mousemove", handleMouseMove);
        document.addEventListener("mouseup", handleMouseUp);
    }
}
//如果handlePointerDragStart偵測到mousemove，此函式會傳遞到updatePointerPosition更新指標位置
function handleMouseMove(event) {
    if (isDraggingStart) {
        updatePointerPosition(startPointer, event);
    }
    if (isDraggingEnd) {
        updatePointerPosition(endPointer, event);
    }
}
//如果handlePointerDragStart偵測到mouseup，此函式會傳遞到updatePointerPosition更新指標位置
function handleMouseUp() {
    isDraggingStart = false;
    isDraggingEnd = false;

    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", handleMouseUp);

    // 計算並設置起始和結束時間基於指標位置
    const startPercent = parseFloat(startPointer.style.left);
    const endPercent = parseFloat(endPointer.style.left);
    const startTime = (startPercent / 100) * without_pose_video.duration;
    const endTime = (endPercent / 100) * without_pose_video.duration;

    // 更新视频的循环范围
    without_pose_video.loopStart = startTime;
    without_pose_video.loopEnd = endTime;
    with_pose_video.loopStart = startTime;
    with_pose_video.loopEnd = endTime;

    without_pose_video.currentTime = without_pose_video.loopStart; // Set the video to start time
    without_pose_video.pause(); // Pause the video
    with_pose_video.currentTime = with_pose_video.loopStart; // Set the video to start time
    with_pose_video.pause(); // Pause the video

    // 监听视频时间更新事件，以确保在达到结束点时暂停视频
    without_pose_video.addEventListener("timeupdate", function() {
        if (without_pose_video.currentTime >= without_pose_video.loopEnd) {
            without_pose_video.pause();
            without_pose_video.currentTime = without_pose_video.loopStart;
            without_pose_video.play();
        }
    });
    with_pose_video.addEventListener("timeupdate", function() {
        console.log("with_pose_video timeupdate event fired.");
        if (with_pose_video.currentTime >= with_pose_video.loopEnd) {
            with_pose_video.pause();
            with_pose_video.currentTime = with_pose_video.loopStart;
            with_pose_video.play();
        }
    });
}

//如果有偵測到mousedown，呼叫handlePointerDragStart
startPointer.addEventListener("mousedown", (e) => handlePointerDragStart(e, startPointer));
endPointer.addEventListener("mousedown", (e) => handlePointerDragStart(e, endPointer));

let posefunction = false
let without_bone_mode = true

let isCameraHidden = false;
let isVideoHidden = false;

function posemode(){
    posefunction = !posefunction;
    displaybutton.textContent = posefunction ? '關閉骨架' : '顯示骨架';
}
// 監聽按鈕點擊事件
displaybutton.addEventListener("click", () => {
    posemode()
    // 切換視頻的顯示狀態
    if (without_bone_mode) {
        without_pose_video.style.display = "none";
        without_pose_video.style.visibility = "hidden";
        with_pose_video.style.display = "block"
        with_pose_video.style.visibility = "visible";
    } else {
        without_pose_video.style.display = "block";
        without_pose_video.style.visibility = "visible";
        with_pose_video.style.display = "none"
        with_pose_video.style.visibility = "hidden";
    }
    // 更新狀態
    without_bone_mode = !without_bone_mode;

    if (isCameraHidden) {
        video5.style.display = "block";
        video5.style.visibility = "visible";
        out5.style.display = "none";
        out5.style.visibility = "hidden";
      } else {
        video5.style.display = "none";
        video5.style.visibility = "hidden";
        out5.style.display = "block";
        out5.style.visibility = "visible";
      }
      // 更新狀態
      isCameraHidden = !isCameraHidden;
});

let countdownInterval; // 在函数外部声明
let countdownfunction = false

//設定是否要開啟倒數
function countdownmode(){
    countdownfunction = !countdownfunction;
    countdownbutton.textContent = countdownfunction ? '關閉倒数' : '開啟倒数';
}

countdownbutton.addEventListener("click", countdownmode)

// 頁面加載時的倒數

var countdownElement = document.getElementById('countdown');
var countdownValue = 3;

function startCountdown() {
    clearInterval(countdownInterval); // 清除先前的倒數

    countdownElement.textContent = countdownValue;
    countdownInterval = setInterval(function () {  
        countdownSound.play();
        countdownValue--;
        if (countdownValue >= 0) {
            countdownElement.textContent = countdownValue;
        } else {
            clearInterval(countdownInterval);
            // 在這裡可以執行播放影片的相關邏輯
            without_pose_video.play();
            with_pose_video.play();
        }
                
    }, countdowntime);    
}

// 點擊播放按鈕開始倒數
toggle.addEventListener('click', function() {
    if (video.paused) {
        if(countdownfunction){
            // 如果影片是暫停狀態，重置倒數值
            countdownValue = 3;
            startCountdown();
        }
        else{
            without_pose_video.play();
            with_pose_video.play();
        }
    } else {
        without_pose_video.pause(); // 暫停影片
        with_pose_video.pause(); // 暫停影片
        countdownValue = 3; // 重置倒數值
    }
});

without_pose_video.addEventListener('click', function() {
    if (video.paused) {
        if(countdownfunction){
            // 如果影片是暫停狀態，重置倒數值
            countdownValue = 3;
            startCountdown();   
        }
        else{
            without_pose_video.play();
            with_pose_video.play();
        }
    } else {
        without_pose_video.pause(); // 暫停影片
        with_pose_video.pause(); // 暫停影片
        countdownValue = 3; // 重置倒數值
    }
});

with_pose_video.addEventListener('click', function() {
    if (video.paused) {
        if(countdownfunction){
            // 如果影片是暫停狀態，重置倒數值
            countdownValue = 3;
            startCountdown();   
        }
        else{
            without_pose_video.play();
            with_pose_video.play();
        }
    } else {
        without_pose_video.pause(); // 暫停影片
        with_pose_video.pause(); // 暫停影片
        countdownValue = 3; // 重置倒數值
    }
});

//播放暫停
//function togglePlay(e) {
	//without_pose_video[without_pose_video.paused ? 'play' : 'pause' ]();
    //with_pose_video[with_pose_video.paused ? 'play' : 'pause' ]();
//}

//toggle.addEventListener('click', togglePlay);
//video.addEventListener('click', togglePlay);

let mediaRecorder;
let recordedChunks = [];

const recordedVideo = document.getElementById('recorded-video');
const startRecordButton = document.getElementById('start-record');
const stopRecordButton = document.getElementById('stop-record');
const downloadLink = document.getElementById('download-link');

startRecordButton.addEventListener('click', () => {
    startRecordButton.disabled = true;
    stopRecordButton.disabled = false;
    recordedChunks = [];

    navigator.mediaDevices
        .getDisplayMedia({ video: true })
        .then((stream) => {
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/mp4' });

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    recordedChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const recordedBlob = new Blob(recordedChunks, { type: 'video/mp4' });
                const url = URL.createObjectURL(recordedBlob);
                recordedVideo.src = url;

                // 添加下載連結
                downloadLink.href = url;
                downloadLink.style.display = 'block';
                downloadLink.download = 'recorded-video.webm'; // 設定下載檔案名稱

                // 清除錄製的片段
                recordedChunks = [];
            };

            mediaRecorder.start();
        })
        .catch((error) => {
            console.error('Error accessing screen:', error);
        });
});

stopRecordButton.addEventListener('click', () => {
    startRecordButton.disabled = false;
    stopRecordButton.disabled = true;
    mediaRecorder.stop();
});
