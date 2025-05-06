<template>
  <div id="all_studyrooms">
    <h1>自习室管理</h1>

    <!-- 添加自习室按钮 -->
    <p>
      <router-link :to="{ name: 'add_studyroom' }" class="btn btn-primary"
      >添加自习室
      </router-link
      >
    </p>

    <!-- 管理员信息与退出按钮 -->
    <div style="position: absolute; top: 20px; right: 20px;">
      <span>管理员 {{ userName }} </span>
      <button @click="logout" class="btn btn-danger">退出</button>
    </div>

    <!-- 修改整体开放时间按钮 -->
    <button class="btn btn-warning" @click="openTimeModal">修改自习室整体开放时间</button>

    <!-- 修改整体开放时间的模态框 -->
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <span @click="closeModal" class="close">&times;</span>
        <h2>修改整体开放时间</h2>

        <div class="form-group">
          <label for="open_time">开放时间</label>
          <input
              type="time"
              class="form-control"
              v-model="open_time"
              id="open_time"
              required
          />
        </div>

        <div class="form-group">
          <label for="close_time">关闭时间</label>
          <input
              type="time"
              class="form-control"
              v-model="close_time"
              id="close_time"
              required
          />
        </div>

        <button class="btn btn-primary" @click="confirmUpdateTime">确定</button>
      </div>
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
              :to="{ name: 'all_seats', params: { studyroom: studyroom } }"
              class="btn btn-info"
          >
            查看
          </router-link>
          <router-link
              :to="{ name: 'edit_studyroom', params: { studyroom: studyroom } }"
              class="btn btn-primary"
          >修改
          </router-link
          >
          <button
              @click="confirmDelete(studyroom)"
              class="btn btn-danger"
          >删除
          </button>
        </td>
      </tr>
      </tbody>
    </table>
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
      showModal: false, // 控制模态框显示
      open_time: "",
      close_time: ""
    };
  },

  created: function () {
    this.fetchStudyroomData();
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

    // 弹出确认框并删除
    confirmDelete(studyroom) {
      const confirmed = window.confirm(`确定删除自习室: ${studyroom.room_name} ？`);
      if (confirmed) {
        this.deleteStudyroom(studyroom);
      }
    },

    // 删除自习室
    deleteStudyroom(studyroom) {
      this.$http
          .delete("http://localhost:8090/studyroom/" + studyroom.id, {
            headers: {
              "Content-Type": "application/json",
            },
          })
          .then(
              (response) => {
                // 删除成功，刷新列表
                this.fetchStudyroomData();
              },
              (response) => {
                alert("删除失败，请稍后再试。");
              }
          );
    },

    // 打开修改整体开放时间的模态框
    openTimeModal() {
      this.showModal = true;
    },

    // 关闭模态框
    closeModal() {
      this.showModal = false;
    },

    // 确认更新时间
    confirmUpdateTime() {
      const confirmed = window.confirm(`确定修改整体开放时间为：${this.open_time}，关闭时间为：${this.close_time} 吗？`);
      if (confirmed) {
        this.updateAllStudyroomsTime();
      }
    },

    // 更新自习室整体开放时间
    updateAllStudyroomsTime() {
      const timestamp = {
        open_time: this.open_time,
        close_time: this.close_time
      };
      this.$http
          .post("http://localhost:8090/studyroom/update_all_time", timestamp, {
            headers: {
              "Content-Type": "application/json",
            },
          })
          .then((response) => {
            alert("修改成功！");
            this.showModal = false;
            this.fetchStudyroomData(); // 刷新列表
          })
          .catch((error) => {
            alert("修改失败！");
          });

    },
  },
};
</script>

<style>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 5px;
  width: 300px;
  text-align: center;
}

.close {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 30px;
  cursor: pointer;
}
</style>