socket = io.connect("/game");

if (typeof user_id != 'undefined') {
    socket.send("subscribe:" + user_id);
}

socket.on("new_invite", function(obj){
    SetNotificationMessage(obj[0], "info");
});

socket.on("game_started", function(obj){
    SetNotificationMessage(obj[0], "info");
});

socket.on("game_over", function(obj){
    SetNotificationMessage(obj[0], "info");
    $(".gameover").animate({opacity: "show"}, "slow");
});

socket.on("opponent_moved", function(obj){
    var data = eval(obj);
    $('#cell' + data[1]).html(data[0]);
    $('#cell' + data[1]).removeClass();
    $('#cell' + data[1]).addClass('checked-' + data[0]);
    SwapUser();
});

function MakeMove(sender, move) {
    if (player == current_player && game_over == "false") {
        if ($(sender).text().trim() == "") {
            $(sender).html(player);
            $(sender).removeClass();
            $(sender).addClass('checked-' + player);
            SwapUser();
            $.post(create_move_url, {'move': move})
        }
    }
}

function SwapUser() {
    var swap = player == "x" ? "o" : "x";
    if (current_player == player) {
        current_player = swap;
        SetNotificationMessage("Your opponents turn!", "warning");
    } else {
        current_player = player;
        SetNotificationMessage("Your turn!", "warning");
    }
}

function SetNotificationMessage(message, status) {
    var $panel = $(".notifications-container #notification-panel");
    $('.panel-body', $panel).html(message);
    $panel.removeClass();
    $panel.addClass('panel panel-' + status);
    $panel.removeClass('hidden');
}
