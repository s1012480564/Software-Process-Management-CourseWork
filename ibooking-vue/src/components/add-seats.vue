<template>
  <div id="add_seat">
    <h1>添加座位</h1>

    <p>
      <router-link :to="{ name: 'all_seats', params: { studyroom: studyroom }  }"
      >返回自习室 {{ studyroom.room_name }} 座位管理页面
      </router-link
      >
    </p>

    <notification v-bind:notifications="notifications"></notification>

    <form v-on:submit.prevent="addSeat">
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
        <button class="btn btn-primary">添加</button>
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
      seat: {
        id: "", // 由后端生成 uid
        studyroom_id: "", // 当前自习室
        seat_name: "",
        position_row: 1,
        position_column: 1,
        status: 1, // 默认未占用
      },
      notifications: [],
    };
  },

  created: function () {
    this.getStudyroom();
    this.seat.studyroom_id = this.studyroom.id;  // 设置 seat 的当前自习室
  },

  methods: {
    getStudyroom: function () {
      this.studyroom = this.$route.params.studyroom;
    },

    addSeat: function () {
      // 清空旧的通知
      this.notifications = [];

      this.$http
          .post("http://localhost:8090/seat", this.seat, {
            headers: {
              "Content-Type": "application/json",
            },
          })
          .then(
              (response) => {
                this.notifications.push({
                  type: "success",
                  message: "座位添加成功",
                });
              },
              (response) => {
                this.notifications.push({
                  type: "error",
                  message: "座位添加失败",
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
