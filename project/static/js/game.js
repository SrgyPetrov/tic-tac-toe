socket = io.connect("/game");

if (typeof user_id != 'undefined') {
  socket.emit('connect', user_id, username);
}

$(window).on("beforeunload", function() {
  socket.emit("disconnect", user_id);
})

socket.on("change_user_list", function(obj){
  delete obj[user_id];
  RedrawUserList(obj)
});

socket.on("new_invite", function(obj){
  message = gettext("You have a new game invite from %s. <br> \
                     <a href='%s' class='btn btn-success invite-link'> Accept</a> \
                     <a href='%s' class='btn btn-danger invite-link' id='decline'> Decline</a>");
  fmessage = interpolate(message, [obj[0], obj[1], obj[2]]);
  SetNotificationMessage(fmessage, "info", true);
});

socket.on("invitation_declined", function(obj){
  message = gettext("%s has declined your invitation.");
  fmessage = interpolate(message, [obj[0]]);
  SetNotificationMessage(fmessage, "danger", true);
});

socket.on("game_started", function(obj){
  message = gettext("A new game with %s has started <a href='%s'>here.</a>");
  fmessage = interpolate(message, [obj[0], obj[1]]);
  SetNotificationMessage(fmessage, "info", true);
});

socket.on("game_over", function(obj){
  message = GetGamoverText(obj[0], obj[1]);
  SetNotificationMessage(message[0], message[1]);
  $(".gameover").animate({opacity: "show"}, "slow");
});

socket.on("refuse", function(obj){
  message = gettext("%s has refused game.");
  fmessage = interpolate(message, [obj[0]]);
  SetNotificationMessage(fmessage, "danger");
  $(".gameover .replay").addClass('hidden');
  $(".gameover .game-refused").removeClass('hidden');
  $(".gameover").animate({opacity: "show"}, "slow");
  $("#active-game-" + obj[1]).remove();
});

socket.on("replay", function(obj){
  message = gettext("%s started game again. <a href='%s' class='btn btn-danger refuse-link'> Refuse</a>");
  fmessage = interpolate(message, [obj[0], obj[1]]);
  ClearPlayfield();
  current_player = obj[2];
  SetNotificationMessage(gettext("Your turn."), 'warning');
  SetNotificationMessage(fmessage, 'info', true);
});

socket.on("opponent_moved", function(obj){
  $('#cell' + obj[1]).html(obj[0]);
  $('#cell' + obj[1]).removeClass().addClass('checked-' + obj[0]);
  if (typeof obj[2] == 'undefined') {
    SetNotificationMessage(gettext("Your turn."), "warning");
  }
  SwapUser();
});

function MakeMove(sender, move) {
  if (player == current_player) {
    RemoveReplayNotification();
    if ($(sender).text().trim() == "") {
      $(sender).html(player);
      $(sender).removeClass().addClass('checked-' + player);
      SwapUser();
      $.post(create_move_url, {'move': move, 'game': game_id, 'user': user_id}, function(data) {
        if (data.length) {
          SetNotificationMessage(data, "warning");
        }
      });
    }
  }
}

function SwapUser() {
  var swap = player == "x" ? "o" : "x";
  if (current_player == player) {
    current_player = swap;
  } else {
    current_player = player;
  }
}

function RemoveReplayNotification() {
  var $link = $('.refuse-link');
  if ($link.length) {
    $link.closest('.panel').remove();
  }
}

function SetNotificationMessage(message, status, create) {
  create = typeof create !== 'undefined' ? create : false;
  var $panel = $(".notifications-container #notification-panel");

  if (create) {
    var $panel = $panel.clone();
    $panel.removeAttr('id')
    $panel.appendTo(".notifications-container");
  }

  $('.panel-body', $panel).html(message);
  $panel.removeClass();
  $panel.addClass('panel panel-' + status);
  $panel.removeClass('hidden');
}

function RedrawUserList(users) {
  var $container = $('#user-list');
  var $links = $('#user-links', $container);
  if($container.length) {
    $links.empty();
    for (var user in users) {
      if (users.hasOwnProperty(user)) {
        $links.append(
          "<a href='javascript:;' class='list-group-item user-invite' data-pk='"
           + user + "'>" + users[user] + "</a>"
        )
      }
    }
  }
  if($links.children().length) {
    $('#title-empty', $container).addClass("hidden");
    $('#title-users-exists', $container).removeClass("hidden");
  }
}

function ClearPlayfield() {
  $(".playfield div").each(function(index) {
    $(this).empty();
    $(this).removeClass();
  });
  $(".gameover").animate({opacity: "hide"}, "slow");
}

function GetGamoverText(player, winner) {
  if (winner && winner == player) {
    return [gettext("You won!"), 'success'];
  } else if (winner && winner != player) {
    return [gettext("You lost the game."), 'danger'];
  } else {
    return [gettext("Its a tie!"), 'info'];
  }
}

$('#user-list').on('click', '.user-invite', function () {
  var $pk = $(this).data('pk');
  $.post(window.location, {'invitee': $pk, 'inviter': user_id}, function(data) {
    if (data.length) {
      try {
        var json_data = JSON.parse(data);
        $.each(json_data, function(i, error) {
          SetNotificationMessage(error[0].message, "danger", true);
        })
      } catch(e) {
         SetNotificationMessage(data, "success", true);
      }
    }
  });
});

$('.notifications-container').on('click', '#decline', function (e) {
  e.preventDefault();
  var $this = $(this)
  var $url = $this.attr('href');
  $.post($url, {}, function(data) {
    if (data.length) {
      $this.closest('.panel').not("#notification-panel").remove();
      SetNotificationMessage(data, "success");
    }
  });
});

$('.game-container').on('click', '.replay', function (e) {
  $.post($(this).data('url'), {}, function(data) {
    if (data.length) {
      ClearPlayfield();
      SetNotificationMessage(data, "warning");
    }
  });
});

$('.active-game').on('click', '.refuse-link', function (e) {
  var $this = $(this)
  var $url = $this.data('url');
  $.post($url, {}, function(data) {
    if (data.length) {
      $this.closest('.panel').remove();
      SetNotificationMessage(data, "success", true);
    }
  });
});
