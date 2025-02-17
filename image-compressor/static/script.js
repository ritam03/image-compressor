let currentTimestamp = "";

document.getElementById("imageInput").addEventListener("change", function () {
    let file = this.files[0];
    if (file) {
        let formData = new FormData();
        formData.append("image", file);

        fetch("/upload", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.image_url) {
                currentTimestamp = data.timestamp;
                document.getElementById("originalImage").src = window.location.origin + data.image_url;
                document.getElementById("originalImage").style.display = "block";
                document.getElementById("originalSize").innerText = "Original Size: " + data.original_size + " KB";

                document.getElementById("compressedImage").style.display = "none";
                document.getElementById("compressedSize").innerText = "";
                document.getElementById("saveButton").classList.add("hidden");
            }
        });
    }
});

function compressImage() {
    if (!currentTimestamp) return;

    let sizeLimit = document.getElementById("sizeLimit").value;
    let formData = new FormData();
    formData.append("size_limit", sizeLimit);
    formData.append("timestamp", currentTimestamp);

    fetch("/compress", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.image_url) {
            document.getElementById("compressedImage").src = window.location.origin + data.image_url;
            document.getElementById("compressedImage").style.display = "block";
            document.getElementById("compressedSize").innerText = "Compressed Size: " + data.compressed_size + " KB";
            document.getElementById("saveButton").classList.remove("hidden");
        }
    });
}

function saveImage() {
    if (!currentTimestamp) return;

    let downloadLink = document.createElement("a");
    downloadLink.href = "/compressed_image/" + currentTimestamp;
    downloadLink.download = "compressed_image.jpg";
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}
