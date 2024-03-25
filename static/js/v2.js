$(document).ready(function () {
    const chatMessages = $("#chat-messages");
    var paragraph = document.getElementById("dataParagraph");
    var dataInfo = paragraph.getAttribute("data-info");

    console.log(dataInfo);
    function scrollToBottom() {
        chatMessages.animate(
            {
                scrollTop: chatMessages[0].scrollHeight,
            },
            500
        );
    }

    function disableChat() {
        $("#chat-input").prop("disabled", true);
        $("#send-button").prop("disabled", true);
        chatMessages.append(
            `<div class="chat-container" id="loading">
        <div class="assistant-image">
          <img src="${window.location.origin}/static/image/3.png" alt="Assistant" class="assistant-image-glow">
        </div>
        <div id="loading-animation" class="chat-message chat-bot" style="width:100%;">
        <i class="fas fa-spinner fa-spin"></i> Loading...</div>
        </div>`
        );
        scrollToBottom();
    }

    function enableChat() {
        $("#chat-input").prop("disabled", false);
        $("#send-button").prop("disabled", false);
        $("#loading").remove();
    }

    function sendMessage() {
        const chatInput = $("#chat-input");
        const userMessage = chatInput.val().trim();

        if (!userMessage) return;

        chatMessages.append(`
        <div class="chat_container_user">
          <div class="chat-message chat-user">
            <div class="message-text">
              ${userMessage}
            </div>
          </div>
        </div>
      `);
        chatInput.val("");
        scrollToBottom();
        disableChat();
        $.post(
            `${window.location.origin}/submit`,
            { user_input: userMessage, user_id: dataInfo },
            function (response) {
                let botMessage = "";

                if (response && typeof response === "object" && response.message) {
                    botMessage = response.message;
                } else if (typeof response === "string") {
                    botMessage = response;
                }

                chatMessages.append(`
          <div class="chat-container">
            <div class="assistant-image">
              <img src="${window.location.origin}/static/image/3.png" alt="Assistant" class="assistant-image-glow">
            </div>
            <div class="chat-message chat-bot">
              <div class="message-text_2"></div>
            </div>
          </div>
        `);

                const imageUrls = getImageUrlsFromText(botMessage);
                preloadImages(imageUrls, function () {
                    function typeBotMessage(message, index) {
                        if (index < message.length) {
                            const currentChar = message.charAt(index);
                            chatMessages.find(".message-text_2:last").append(currentChar);
                            if (index === 0) {
                                $("#loading").remove();
                                scrollToBottom();
                            }
                            setTimeout(() => {
                                typeBotMessage(message, index + 1);
                            }, 50);
                        } else {
                            enableChat();
                            scrollToBottom();
                        }
                    }

                    typeBotMessage(botMessage, 0);
                });
            }
        ).fail(function () {
            chatMessages.append(
                `<div class="chat-container">
            <div class="assistant-image">
              <img src="${window.location.origin}/static/image/3.png" alt="Assistant" class="assistant-image-glow">
            </div>
            <div class="chat-message chat-bot">
              <div class="message-text">
                We're sorry, but there's a slight hiccup in the response.
              </div>
            </div>
          </div>
        `
            );
            scrollToBottom();
            console.error("There was an error in sending the message!");

            enableChat();
            $("#loading").remove();
        });
    }

    function getImageUrlsFromText(text) {
        const imageUrls = [];
        const imgRegex = /<img[^>]+src="([^">]+)"/g;
        let match;
        while ((match = imgRegex.exec(text))) {
            imageUrls.push(match[1]);
        }
        return imageUrls;
    }

    // Function to preload images
    function preloadImages(imageUrls, callback) {
        let loaded = 0;
        const total = imageUrls.length;
        if (total === 0) {
            callback();
        }
        imageUrls.forEach((url) => {
            const img = new Image();
            img.src = url;
            img.onload = () => {
                loaded++;
                if (loaded === total) {
                    callback();
                }
            };
        });
    }

    $("#send-button").click(function () {
        sendMessage();
    });

    $("#chat-input").keypress(function (e) {
        if (e.which === 13) {
            e.preventDefault();
            sendMessage();
        }
    });
});
