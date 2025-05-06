<template>
  <div id="all_seats">
    <h1>自习室 {{ studyroom.room_name }} 座位管理</h1>

    <p>
      <router-link :to="{ name: 'all_studyrooms' }"
      >返回自习室管理页面
      </router-link
      >
    </p>

    <!-- 添加座位按钮 -->
    <p>
      <router-link
          :to="{ name: 'add_seat', params: { studyroom: studyroom }  }"
          class="btn btn-primary"
      >添加座位
      </router-link
      >
    </p>

    <!-- 座位列表和搜索框 -->
    <div class="form-group">
      <input
          type="text"
          name="search"
          v-model="seatSearch"
          placeholder="输入座位名称筛选自习室"
          class="form-control"
          v-on:keyup="searchSeats"
      />
    </div>

    <table class="table table-hover">
      <thead>
      <tr>
        <th>ID</th>
        <th>座位名称</th>
        <th>座位行号</th>
        <th>座位列号</th>
        <th>当前座位状态</th>
      </tr>
      </thead>

      <tbody>
      <tr v-for="seat in seats">
        <td>{{ seat.id }}</td>
        <td>{{ seat.seat_name }}</td>
        <td>{{ seat.position_row }}</td>
        <td>{{ seat.position_column }}</td>
        <td>
          <span v-if="seat.status === 1">1（未占用）</span>
          <span v-if="seat.status === 2">2（已占用）</span>
          <span v-if="seat.status === 3">3（已签到）</span>
        </td>
        <td>
          <router-link
              :to="{ name: 'edit_seat', params: { seat: seat, studyroom: studyroom } }"
              class="btn btn-primary"
          >修改
          </router-link
          >
          <button
              @click="confirmDelete(seat)"
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
      studyroom: {},
      notifications: [],
      seats: [],
      originalSeats: [],
      seatSearch: "",
    };
  },

  created: function () {
    this.getStudyroom();
    this.fetchSeatData();
  },

  methods: {
    getStudyroom: function () {
      this.studyroom = this.$route.params.studyroom;
    },

    fetchSeatData: function () {
      this.$http.get("http://127.0.0.1:8090/seat/list/" + this.studyroom.id).then(
          (response) => {
            this.seats = response.body.data;
            this.originalSeats = this.seats;
          },
          (response) => {
          }
      );
    },

    searchSeats: function () {
      if (this.seatSearch === "") {
        this.seats = this.originalSeats;
        return;
      }

      var searchedSeats = [];
      for (var i = 0; i < this.originalSeats.length; i++) {
        var seatName = this.originalSeats[i]["seat_name"].toLowerCase();
        if (seatName.indexOf(this.seatSearch.toLowerCase()) >= 0) {
          searchedSeats.push(this.originalSeats[i]);
        }
      }

      this.seats = searchedSeats;
    },

    // 弹出确认框并删除
    confirmDelete(seat) {
      const confirmed = window.confirm(`确定删除座位: ${seat.seat_name} ？`);
      if (confirmed) {
        this.deleteSeat(seat);
      }
    },

    // 删除自习室
    deleteSeat(seat) {
      this.$http
          .delete("http://localhost:8090/seat/" + seat.id, {
            headers: {
              "Content-Type": "application/json",
            },
          })
          .then(
              (response) => {
                // 删除成功，刷新列表
                this.fetchSeatData();
              },
              (response) => {
                alert("删除失败，请稍后再试。");
              }
          );
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