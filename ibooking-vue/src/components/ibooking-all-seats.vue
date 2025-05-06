<template>
  <div id="ibooking_all_seat">
    <h1>自习室 {{ studyroom.room_name }} 全部座位</h1>

    <p>
      <router-link :to="{ name: 'ibooking_index' }"
      >返回自习室预约主页
      </router-link
      >
    </p>

    <!-- 期望预约时间筛选 -->
    <div class="form-group d-flex align-items-center">
      <label class="mr-2">期望开始时间：</label>
      <div class="d-flex">
        <select v-model="filterBeginHour" class="form-control time-select" required
                @change="handleHourChange('filterBegin')">
          <option v-for="hour in hours" :key="hour" :value="hour">{{ hour }}</option>
        </select>
        <span class="time-separator">:</span>
        <select v-model="filterBeginMinute" class="form-control time-select" required
                :disabled="filterBeginHour !== '23'">
          <option v-if="filterBeginHour !== '23'" value="00">00</option>
          <option v-if="filterBeginHour === '23'" value="00">00</option>
          <option v-if="filterBeginHour === '23'" value="59">59</option>
        </select>
      </div>
    </div>

    <div class="form-group d-flex align-items-center">
      <label class="mr-2">期望结束时间：</label>
      <div class="d-flex">
        <select v-model="filterEndHour" class="form-control time-select" required
                @change="handleHourChange('filterEnd')">
          <option v-for="hour in hours" :key="hour" :value="hour">{{ hour }}</option>
        </select>
        <span class="time-separator">:</span>
        <select v-model="filterEndMinute" class="form-control time-select" required
                :disabled="filterEndHour !== '23'">
          <option v-if="filterEndHour !== '23'" value="00">00</option>
          <option v-if="filterEndHour === '23'" value="00">00</option>
          <option v-if="filterEndHour === '23'" value="59">59</option>
        </select>
      </div>
    </div>

    <div class="form-group mt-2">
      <button class="btn btn-primary" @click="filterSeatsByTime">按时间筛选</button>
      <button class="btn btn-secondary" @click="resetSeatFilter">清除筛选</button>
    </div>

    <!-- 座位列表和搜索框 -->
    <div class="form-group">
      <input
          type="text"
          name="search"
          v-model="seatSearch"
          placeholder="输入座位名称筛选座位"
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
          <span v-if="seat.status === 1">未占用</span>
          <span v-if="seat.status === 2">已占用</span>
          <span v-if="seat.status === 3">已签到</span>
        </td>
        <td>
          <router-link
              :to="{ name: 'ibooking_all_seat_bookings', params: { seat: seat, studyroom: studyroom } }"
              class="btn btn-info"
          >
            查看
          </router-link>
          <button
              class="btn btn-primary"
              @click="openBookingModal(seat)"
          >预约
          </button
          >
          <button
              class="btn btn-danger"
              @click="opengrabBookingModal(seat)"
              :disabled="seat.status !== 1"
          >抢位
          </button>
        </td>
      </tr>
      </tbody>
    </table>

    <!-- 预约弹出框。只能整点预约，特别地最后一个小时可以预约到 23:59 -->
    <div v-if="showModal" class="modal-overlay" @click="closeBookingModal">
      <div class="modal-content" @click.stop>
        <h3>预约座位: {{ selectedSeat.seat_name }}</h3>
        <form @submit.prevent="submitBooking">
          <div class="form-group d-flex align-items-center">
            <label class="mr-2" for="begin_time">开始时间：</label>
            <div class="d-flex">
              <select v-model="beginHour" id="begin_hour" required @change="handleHourChange('begin')">
                <option v-for="hour in hours" :key="hour" :value="hour">{{ hour }}</option>
              </select>
              <select v-model="beginMinute" id="begin_minute" required :disabled="beginHour !== '23'">
                <option v-if="beginHour !== '23'" value="00">00</option>
                <option v-if="beginHour === '23'" value="00">00</option>
                <option v-if="beginHour === '23'" value="59">59</option>
              </select>
            </div>
          </div>
          <div class="form-group d-flex align-items-center">
            <label class="mr-2" for="end_time">结束时间：</label>
            <div class="d-flex">
              <select v-model="endHour" id="end_hour" required @change="handleHourChange('end')">
                <option v-for="hour in hours" :key="hour" :value="hour">{{ hour }}</option>
              </select>
              <select v-model="endMinute" id="end_minute" required :disabled="endHour !== '23'">
                <option v-if="endHour !== '23'" value="00">00</option>
                <option v-if="endHour === '23'" value="00">00</option>
                <option v-if="endHour === '23'" value="59">59</option>
              </select>
            </div>
          </div>
          <button type="submit" class="btn btn-success">预约</button>
          <button type="button" class="btn btn-secondary" @click="closeBookingModal">取消</button>
        </form>
        <p v-if="bookingMessage" :class="{'text-success': bookingSuccess, 'text-danger': !bookingSuccess}">
          {{ bookingMessage }}</p>
      </div>
    </div>

    <!-- 抢位弹出框，和预约类似 -->
    <div v-if="showGrabModal" class="modal-overlay" @click="closeGrabBookingModal">
      <div class="modal-content" @click.stop>
        <h3>抢位座位: {{ selectedGrabSeat.seat_name }}</h3>
        <form @submit.prevent="submitGrabBooking">
          <div class="form-group d-flex align-items-center">
            <label class="mr-2" for="end_time">结束时间：</label>
            <div class="d-flex">
              <select v-model="grabEndHour" id="end_hour" required @change="handleHourChange('grabEnd')">
                <option v-for="hour in hours" :key="hour" :value="hour">{{ hour }}</option>
              </select>
              <select v-model="grabEndMinute" id="end_minute" required :disabled="grabEndHour !== '23'">
                <option v-if="grabEndHour !== '23'" value="00">00</option>
                <option v-if="grabEndHour === '23'" value="00">00</option>
                <option v-if="grabEndHour === '23'" value="59">59</option>
              </select>
            </div>
          </div>
          <button type="submit" class="btn btn-danger">抢位</button>
          <button type="button" class="btn btn-secondary" @click="closeGrabBookingModal">取消</button>
        </form>
        <p v-if="grabBookingMessage" :class="{'text-success': grabBookingSuccess, 'text-danger': !grabBookingSuccess}">
          {{ grabBookingMessage }}</p>
      </div>
    </div>

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
      showModal: false,
      selectedSeat: null,
      beginHour: "00",
      beginMinute: "00",
      endHour: "00",
      endMinute: "00",
      bookingMessage: "",
      bookingSuccess: false,
      hours: Array.from({length: 24}, (_, i) => String(i).padStart(2, "0")), // 生成 00 到 23 的小时列表
      filterBeginHour: "00",
      filterBeginMinute: "00",
      filterEndHour: "00",
      filterEndMinute: "00",
      showGrabModal: false,  // 用于显示抢位弹窗
      selectedGrabSeat: null,  // 选中的抢位座位
      grabEndHour: "00",  // 抢位结束时间的小时
      grabEndMinute: "00",  // 抢位结束时间的分钟
      grabBookingMessage: "",  // 提示信息
      grabBookingSuccess: false,  // 抢位是否成功
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

    openBookingModal(seat) {
      this.selectedSeat = seat;
      this.showModal = true;
    },

    closeBookingModal() {
      this.showModal = false;
      this.selectedSeat = null;
      this.beginHour = "00";
      this.beginMinute = "00";
      this.endHour = "00";
      this.endMinute = "00";
      this.bookingMessage = "";
    },

    handleHourChange(type) {
      if (type === 'begin') {
        if (this.beginHour !== '23') {
          this.beginMinute = '00';
        }
      } else if (type === 'end') {
        if (this.endHour !== '23') {
          this.endMinute = '00';
        }
      } else if (type === 'filterBegin') {
        if (this.filterBeginHour !== '23') {
          this.filterBeginMinute = '00';
        }
      } else if (type === 'filterEnd') {
        if (this.filterEndHour !== '23') {
          this.filterEndMinute = '00';
        }
      } else if (type === 'grabEnd') {
        if (this.grabEndHour !== '23') {
          this.grabEndMinute = '00';
        }
      }
    },

    async submitBooking() {
      const bookingData = {
        user_id: this.$route.params.userId,
        seat_id: this.selectedSeat.id,
        begin_time: `${this.beginHour}:${this.beginMinute}`,
        end_time: `${this.endHour}:${this.endMinute}`,
      };

      try {
        const response = await this.$http.post("http://127.0.0.1:8090/booking/", bookingData);
        if (response.body.status === 200) {
          this.bookingSuccess = true;
          this.bookingMessage = "预约成功！请在预约开始后 15 分钟内签到，否则预约无效！";
          window.alert("预约成功！请在预约开始后 15 分钟内签到，否则预约无效！");
          this.closeBookingModal();
        } else {
          this.bookingSuccess = false;
          this.bookingMessage = response.body.detail || "预约失败，请稍后再试。";
        }
      } catch (error) {
        this.bookingSuccess = false;
        this.bookingMessage = error.body.detail || "预约失败，请稍后再试。";
      }
    },

    filterSeatsByTime() {
      const begin_time = `${this.filterBeginHour}:${this.filterBeginMinute}`;
      const end_time = `${this.filterEndHour}:${this.filterEndMinute}`;
      const user_id = this.$route.params.userId;

      const url = `http://127.0.0.1:8090/seat/list/available/${this.studyroom.id}?user_id=${user_id}&begin_time=${begin_time}&end_time=${end_time}`;

      this.$http.get(url).then(
          (response) => {
            this.seats = response.body.data;
          },
          (response) => {
            this.seats = [];
            window.alert("没有符合条件的座位");
          }
      );
    },

    resetSeatFilter() {
      this.filterBeginHour = "00";
      this.filterBeginMinute = "00";
      this.filterEndHour = "00";
      this.filterEndMinute = "00";
      this.seatSearch = "";
      this.fetchSeatData();
    },

    // 打开抢位的模态框
    opengrabBookingModal(seat) {
      this.selectedGrabSeat = seat;
      this.showGrabModal = true;
    },

    // 关闭抢位模态框
    closeGrabBookingModal() {
      this.showGrabModal = false;
      this.selectedGrabSeat = null;
      this.grabEndHour = "00";
      this.grabEndMinute = "00";
      this.grabBookingMessage = "";
    },

    // 提交抢位请求
    async submitGrabBooking() {
      // 动态获取当前时间
      const now = new Date();
      const beginHour = String(now.getHours()).padStart(2, "0");
      const beginMinute = String(now.getMinutes()).padStart(2, "0");
      const currentBeginTime = `${beginHour}:${beginMinute}`;  // 格式化为 "HH:mm"

      const grabBookingData = {
        user_id: this.$route.params.userId,
        seat_id: this.selectedGrabSeat.id,
        begin_time: currentBeginTime,
        end_time: `${this.grabEndHour}:${this.grabEndMinute}`,
      };

      try {
        const response = await this.$http.post("http://127.0.0.1:8090/booking/grab/", grabBookingData);
        if (response.body.status === 200) {
          this.grabBookingSuccess = true;
          this.grabBookingMessage = "抢位成功！请在 5 分钟内签到，否则抢位无效！";
          window.alert("抢位成功！请在 5 分钟内签到，否则抢位无效！");
          this.closeGrabBookingModal();
        } else {
          this.grabBookingSuccess = false;
          this.grabBookingMessage = response.body.detail || "抢位失败，请稍后再试。";
        }
      } catch (error) {
        this.grabBookingSuccess = false;
        this.grabBookingMessage = error.body.detail || "抢位失败，请稍后再试。";
      }
    },

  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  width: 300px;
}

/* 调整 select 框的大小 */
.time-select {
  width: 50px;
  padding: 5px;
  font-size: 14px;
}

/* 对于时间框之间的间距进行调整 */
.time-separator {
  margin: 0 5px;
  font-size: 16px;
}

/* 调整 label 和 select 的排列 */
.d-flex {
  display: flex;
  align-items: center;
}

.mr-2 {
  margin-right: 10px;
}

</style>