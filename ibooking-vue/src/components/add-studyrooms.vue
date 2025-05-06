<template>
  <div id="add_studyroom">
    <h1>添加自习室</h1>

    <p>
      <router-link :to="{ name: 'all_studyrooms' }"
      >返回自习室管理页面
      </router-link
      >
    </p>

    <notification v-bind:notifications="notifications"></notification>

    <form v-on:submit.prevent="addStudyroom">
      <div class="form-group">
        <label for="studyroom_id">ID</label>
        <input
            type="text"
            class="form-control"
            disabled
            v-model="studyroom.id"
            id="studyroom_id"
        />
      </div>

      <div class="form-group">
        <label for="studyroom_name">自习室名称</label>
        <input
            type="text"
            class="form-control"
            v-model="studyroom.room_name"
            id="studyroom_name"
            required
        />
      </div>

      <div class="form-group">
        <label for="room_row">行数</label>
        <input
          type="number"
          class="form-control"
          v-model="studyroom.room_row"
          id="room_row"
          required
        />
      </div>

      <div class="form-group">
        <label for="room_column">列数</label>
        <input
          type="number"
          class="form-control"
          v-model="studyroom.room_column"
          id="room_column"
          required
        />
      </div>

      <div class="form-group">
        <label for="open_time">开放时间</label>
        <input
          type="time"
          class="form-control"
          v-model="studyroom.open_time"
          id="open_time"
          required
        />
      </div>

      <div class="form-group">
        <label for="close_time">关闭时间</label>
        <input
          type="time"
          class="form-control"
          v-model="studyroom.close_time"
          id="close_time"
          required
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
      studyroom: {
        id: "", // 由后端生成 uid
        room_name: "",
        room_row: 10,
        room_column: 10,
        open_time: "06:00",
        close_time: "23:59",
      },
      notifications: [],
    };
  },

  methods: {
    addStudyroom: function () {
      // 清空旧的通知
      this.notifications = [];

      this.$http
          .post("http://localhost:8090/studyroom", this.studyroom, {
            headers: {
              "Content-Type": "application/json",
            },
          })
          .then(
              (response) => {
                this.notifications.push({
                  type: "success",
                  message: "自习室添加成功",
                });
              },
              (response) => {
                this.notifications.push({
                  type: "error",
                  message: "自习室添加失败",
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
