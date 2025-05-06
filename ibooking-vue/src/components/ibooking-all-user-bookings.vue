<template>
  <div id="ibooking_all_seat_bookings">
    <h1>我的预约</h1>

    <p>
      <router-link :to="{ name: 'ibooking_index'}"
      >返回自习室预约主页
      </router-link
      >
    </p>

    <table class="table table-hover">
      <thead>
      <tr>
        <th>ID</th>
        <th>自习室名称</th>
        <th>座位名称</th>
        <th>开始时间</th>
        <th>结束时间</th>
        <th>活跃状态</th>
      </tr>
      </thead>

      <tbody>
      <tr v-for="booking in bookings">
        <td>{{ booking.id }}</td>
        <td>{{ booking.room_name }}</td> <!-- 显示自习室名称 -->
        <td>{{ booking.seat_name }}</td> <!-- 显示座位名称 -->
        <td>{{ booking.begin_time }}</td>
        <td>{{ booking.end_time }}</td>
        <td>
          <span v-if="booking.alive === 0">已过期</span>
          <span v-if="booking.alive === 1">进行中</span>
        </td>
        <td>
          <span v-if="booking.alive === 1"><button
              @click="SignIn(booking)"
              class="btn btn-primary"
          >签到</button></span>
          <button
              @click="confirmDelete(booking)"
              class="btn btn-danger"
          ><span v-if="booking.alive === 0">删除记录</span>
            <span v-if="booking.alive === 1">取消预约</span>
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
      userID: {},
      bookings: [],
    };
  },

  created: function () {
    this.getUserId();
    this.fetchBookingData();
  },

  methods: {
    getUserId: function () {
      this.userId = this.$route.params.userId;
    },

    fetchBookingData: function () {
      this.$http.get("http://127.0.0.1:8090/booking/user/joint/" + this.userId).then(
          (response) => {
            this.bookings = response.body.data;
          },
          (response) => {
          }
      );
    },

    // 弹出确认框并删除
    confirmDelete(booking) {
      const prompt = booking.alive === 0 ? '确定删除记录？' : '确定取消预约？';
      const confirmed = window.confirm(prompt);
      if (confirmed) {
        this.deleteBooking(booking);
      }
    },

    // 删除自习室
    deleteBooking(booking) {
      this.$http
          .delete("http://localhost:8090/booking/" + booking.id, {
            headers: {
              "Content-Type": "application/json",
            },
          })
          .then(
              (response) => {
                // 删除成功，刷新列表
                this.fetchBookingData();
              },
              (response) => {
                alert("删除记录/取消预约失败，请稍后再试。");
              }
          );
    },

    // 签到
    SignIn(booking) {
      // 查询座位状态
      this.$http.get("http://127.0.0.1:8090/seat/" + booking.seat_id).then(
          (response) => {
            const seatStatus = response.body.data.status;

            // 如果座位已经签到
            if (seatStatus === 3) {
              alert("您已成功签到，无需重复签到。");
            } else {
              // 否则，签到
              this.$http
                  .put(
                      `http://127.0.0.1:8090/seat/status/${booking.seat_id}?status=3`,
                      {},
                      {
                        headers: {
                          "Content-Type": "application/json",
                        },
                      }
                  )
                  .then(
                      (response) => {
                        alert("您已成功签到！");
                        // 成功签到后，可以选择更新列表或其他操作
                        this.fetchBookingData();
                      },
                      (error) => {
                        alert("签到失败，请稍后再试。");
                      }
                  );
            }
          },
          (error) => {
            alert("无法查询座位状态，请稍后再试。");
          }
      );
    }

  },
};
</script>
