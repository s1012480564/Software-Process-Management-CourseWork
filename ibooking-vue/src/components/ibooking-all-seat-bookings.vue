<template>
  <div id="ibooking_all_seat_bookings">
    <h1>自习室 {{ studyroom.room_name }} 座位 {{ seat.seat_name }} 全部已有预约</h1>

    <p>
      <router-link :to="{ name: 'ibooking_all_seats', params: { studyroom: studyroom }  }"
      >返回自习室 {{ studyroom.room_name }} 全部座位
      </router-link
      >
    </p>

    <table class="table table-hover">
      <thead>
      <tr>
        <th>ID</th>
        <th>开始时间</th>
        <th>结束时间</th>
        <th>活跃状态</th>
      </tr>
      </thead>

      <tbody>
      <tr v-for="booking in bookings">
        <td>{{ booking.id }}</td>
        <td>{{ booking.begin_time }}</td>
        <td>{{ booking.end_time }}</td>
        <td>
          <span v-if="booking.alive === 0">已过期</span>
          <span v-if="booking.alive === 1">进行中</span>
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
      seat: {},
      bookings: [],
    };
  },

  created: function () {
    this.getStudyroom();
    this.getSeat();
    this.fetchBookingData();
  },

  methods: {
    getStudyroom: function () {
      this.studyroom = this.$route.params.studyroom;
    },

    getSeat: function () {
      this.seat = this.$route.params.seat;
    },

    fetchBookingData: function () {
      this.$http.get("http://127.0.0.1:8090/booking/seat/" + this.seat.id).then(
          (response) => {
            this.bookings = response.body.data;
          },
          (response) => {
          }
      );
    },
  },
};
</script>
