(function () {
  'use strict';
  var serviceId = 'inhouse';
  angular.module('app').service(serviceId, [
    'common',
    inhouse
  ]);
  function inhouse(common) {
    var $q = common.$q;
    var title = '';
    var league_title = '';
    var team_title = '';
    return {
      setTitle: setTitle,
      getLeagueTitle: getLeagueTitle,
      setLeagueTitle: setLeagueTitle,
      getTeamTitle: getTeamTitle,
      setTeamTitle: setTeamTitle,
      getTitle: getTitle,
      setDate: setDate
    };
    function getLeagueTitle() {
      return league_title;
    }
    function setLeagueTitle(data) {
      league_title = data;
    }
    function getTeamTitle() {
      return team_title;
    }
    function setTeamTitle(data) {
      team_title = data;
    }
    function setTitle(data) {
      title = data;
    }
    function getTitle() {
      return title;
    }
    function setDate(value) {
      return moment.utc(value).format('ddd hh:mm a');
    }
  }
}());