<template>
  <div id="ibooking_index">
    <h1>自习室预约</h1>

    <!-- 添加自习室按钮 -->
    <p>
      <router-link :to="{ name: 'ibooking_all_user_bookings', params: { userId: userId }  }" class="btn btn-primary"
      >我的预约
      </router-link
      >
    </p>

    <div style="position: absolute; top: 20px; right: 20px;">
      <span>用户 {{ userName }} </span>
      <button @click="logout" class="btn btn-danger">退出</button>
    </div>

    <!-- 自习室列表和搜索框 -->
    <div class="form-group">
      <input
          type="text"
          name="search"
          v-model="studyroomSearch"
          placeholder="输入自习室名称筛选自习室"
          class="form-control"
          v-on:keyup="searchStudyrooms"
      />
    </div>

    <table class="table table-hover">
      <thead>
      <tr>
        <th>ID</th>
        <th>自习室名称</th>
        <th>座位行数</th>
        <th>座位列数</th>
        <th>开放时间(每天)</th>
        <th>关闭时间(每天)</th>
      </tr>
      </thead>

      <tbody>
      <tr v-for="studyroom in studyrooms">
        <td>{{ studyroom.id }}</td>
        <td>{{ studyroom.room_name }}</td>
        <td>{{ studyroom.room_row }}</td>
        <td>{{ studyroom.room_column }}</td>
        <td>{{ studyroom.open_time }}</td>
        <td>{{ studyroom.close_time }}</td>
        <td>
          <router-link
              :to="{ name: 'ibooking_all_seats', params: { studyroom: studyroom, userId: userId } }"
              class="btn btn-info"
          >
            查看
          </router-link>
        </td>
      </tr>
      </tbody>
    </table>

    <!-- 通知消息的悬浮提醒框 -->
    <div v-if="notificationMessage" class="notification-box">
      <p>{{ notificationMessage }}</p>
      <button @click="closeNotification" class="close-btn">X</button>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      studyrooms: [],
      originalStudyrooms: [],
      studyroomSearch: "",
      userId: localStorage.getItem("userId"), // 获取存储的 userId
      userName: localStorage.getItem("userName"), // 获取 userName
      notificationMessage: "", // 用于存储通知内容
    };
  },

  created: function () {
    this.fetchStudyroomData();
    this.connectSSE(); // 连接到 SSE 推送服务
  },

  methods: {
    // 退出方法
    logout() {
      // 清除 localStorage 中的用户信息
      localStorage.removeItem("userId");
      localStorage.removeItem("userRole");
      localStorage.removeItem("userName");

      // 跳转到 login 页面
      this.$router.push({name: 'login'});
    },

    fetchStudyroomData: function () {
      this.$http.get("http://127.0.0.1:8090/studyroom/list").then(
          (response) => {
            this.studyrooms = response.body.data;
            this.originalStudyrooms = this.studyrooms;
          },
          (response) => {
          }
      );
    },

    searchStudyrooms: function () {
      if (this.studyroomSearch === "") {
        this.studyrooms = this.originalStudyrooms;
        return;
      }

      var searchedStudyrooms = [];
      for (var i = 0; i < this.originalStudyrooms.length; i++) {
        var studyroomName = this.originalStudyrooms[i]["room_name"].toLowerCase();
        if (studyroomName.indexOf(this.studyroomSearch.toLowerCase()) >= 0) {
          searchedStudyrooms.push(this.originalStudyrooms[i]);
        }
      }

      this.studyrooms = searchedStudyrooms;
    },

    // SSE 连接
    connectSSE() {
      const eventSource = new EventSource(`http://127.0.0.1:8090/notification/${this.userId}`);

      eventSource.onmessage = (event) => {
        this.notificationMessage = event.data.replace(/^data: /, ''); // 更新通知内容。替换掉前缀的 "data: "
      };

      eventSource.onerror = (error) => {
        console.error("SSE Error:", error);
      };
    },

    // 关闭通知框
    closeNotification() {
      this.notificationMessage = ""; // 清空通知内容
    },

  },
};
</script>


<style scoped>
.notification-box {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: #ffcc00;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.close-btn {
  background: none;
  border: none;
  color: black;
  font-weight: bold;
  cursor: pointer;
  font-size: 16px;
}
</style>