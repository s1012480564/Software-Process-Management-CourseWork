<template>
  <div id="edit_seat">
    <h1>座位信息 {{ originalSeat.seat_name }} 修改</h1>

    <p>
      <router-link :to="{ name: 'all_seats', params: { studyroom: studyroom } }"
      >返回自习室 {{ studyroom.room_name }} 座位管理页面
      </router-link
      >
    </p>

    <notification v-bind:notifications="notifications"></notification>

    <form v-on:submit.prevent="editSeat">
      <div class="form-group">
        <label for="seat_id">ID</label>
        <input
            type="text"
            class="form-control"
            disabled
            v-model="seat.id"
            id="seat_id"
        />
      </div>

      <div class="form-group">
        <label for="studyroom_id">自习室ID</label>
        <input
            type="text"
            class="form-control"
            disabled
            v-model="studyroom.id"
            id="studyroom_id"
        />
      </div>

      <div class="form-group">
        <label for="seat_name">座位名称</label>
        <input
            type="text"
            class="form-control"
            v-model="seat.seat_name"
            id="seat_name"
            required
        />
      </div>

      <div class="form-group">
        <label for="seat_row">行号</label>
        <input
            type="number"
            class="form-control"
            v-model="seat.position_row"
            id="seat_row"
            required
        />
      </div>

      <div class="form-group">
        <label for="seat_column">列号</label>
        <input
            type="number"
            class="form-control"
            v-model="seat.position_column"
            id="seat_column"
            required
        />
      </div>

      <div class="form-group">
        <label for="seat_status">当前座位状态</label>
        <input
            type="number"
            class="form-control"
            disabled
            v-model="seat.status"
            id="seat_status"
        />
      </div>

      <div class="form-group">
        <button class="btn btn-primary">修改</button>
      </div>
    </form>
  </div>
</template>

<script>
import Notification from "./notifications.vue";

export default {
  data() {
    return {
      studyroom: {},
      seat: {},
      originalSeat: {},
      notifications: [],
    };
  },

  created: function () {
    this.getStudyroom();
    this.getSeat();
  },

  methods: {
    getStudyroom: function () {
      this.studyroom = this.$route.params.studyroom;
    },
    getSeat: function () {
      this.originalSeat = Object.assign({}, this.$route.params.seat);
      this.seat = this.$route.params.seat;
    },

    editSeat: function () {
      // 清空旧的通知
      this.notifications = [];

      this.$http
          .put("http://localhost:8090/seat/" + this.seat.id, this.seat, {
            headers: {
              "Content-Type": "application/json",
            },
          })
          .then(
              (response) => {
                // 修改成功后，更新 originalSeat
                this.originalSeat = Object.assign({}, this.seat);

                this.notifications.push({
                  type: "success",
                  message: "座位信息修改成功",
                });
              },
              (response) => {
                this.notifications.push({
                  type: "error",
                  message: "座位信息修改失败",
                });
              }
          );
    },
  },

  components: {
    notification: Notification,
  },
};
</script>
