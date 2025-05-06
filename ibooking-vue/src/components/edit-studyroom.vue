<template>
  <div id="edit_studyroom">
    <h1>自习室 {{ originalStudyroom.room_name }} 信息修改</h1>

    <p>
      <router-link :to="{ name: 'all_studyrooms' }"
      >返回自习室管理页面
      </router-link
      >
    </p>

    <notification v-bind:notifications="notifications"></notification>

    <form v-on:submit.prevent="editStudyroom">
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
      originalStudyroom: {},
      notifications: [],
    };
  },

  created: function () {
    this.getStudyroom();
  },

  methods: {
    getStudyroom: function () {
      this.originalStudyroom = Object.assign({}, this.$route.params.studyroom);
      this.studyroom = this.$route.params.studyroom;
    },

    editStudyroom: function () {
      // 清空旧的通知
      this.notifications = [];

      this.$http
          .put("http://localhost:8090/studyroom/" + this.studyroom.id, this.studyroom, {
            headers: {
              "Content-Type": "application/json",
            },
          })
          .then(
              (response) => {
                // 修改成功后，更新 originalStudyroom
                this.originalStudyroom = Object.assign({}, this.studyroom);

                this.notifications.push({
                  type: "success",
                  message: "自习室信息修改成功",
                });
              },
              (response) => {
                this.notifications.push({
                  type: "error",
                  message: "自习室信息修改失败",
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
