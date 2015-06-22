socket = io.connect("/game");

socket.on("message", function(obj){
    if (obj.type == "message") {
        var data = eval(obj.data);

        if (data[0] == "new_invite") {
            SetNotificationMessage(data[1], "info");
        }
        else if (data[0] == "game_started") {
            SetNotificationMessage("A new game has started <a href='" + data[1] + "'>here</a>", "info");
        }
        else if (data[0] == "game_over") {
            if (data[1] == game_id) {
                winner = data[2];
                game_over = true;

                if (data[2] == player) {
                    SetNotificationMessage("You won!", "success");
                } else if (data[2] != player) {
                    SetNotificationMessage("You lost the game.", "danger");
                } else {
                    SetNotificationMessage("Its a tie!", "info");
                }
            }
            else {
                SetNotificationMessage("A game has finished <a href='" + data[1] + "'>here</a>", "info");
            }
            $('.playfield .gameover').removeClass('hidden');
        }
        else if (data[0] == "opponent_moved") {
            if (data[1] == game_id) {
                $('#cell' + data[3]).html(data[2]);
                $('#cell' + data[3]).removeClass();
                $('#cell' + data[3]).addClass('checked-' + data[2]);
                SwapUser();
            }
        }
    }
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

if (typeof user_id != 'undefined') {
    socket.send("subscribe:" + user_id);
}

function SetNotificationMessage(message, status) {
    var $panel = $(".notifications-container #notification-panel");
    $('.panel-body', $panel).html(message);
    $panel.removeClass();
    $panel.addClass('panel panel-' + status);
    $panel.removeClass('hidden');
}
