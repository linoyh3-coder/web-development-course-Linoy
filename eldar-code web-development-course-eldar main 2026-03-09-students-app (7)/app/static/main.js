"use strict"

{
    // get reference to the students table body
    const tbody = document.getElementById("tbody");
    // get reference to inputs
    const idBox = document.getElementById("idBox");
    const nameBox = document.getElementById("nameBox");
    const ageBox = document.getElementById("ageBox");
    // get reference to buttons
    const btAdd = document.getElementById("btAdd");
    const btUpdate = document.getElementById("btUpdate");
    const btDelete = document.getElementById("btDelete");

    // update student
    btUpdate.addEventListener("click", async function () {
        const id = +idBox.value;
        const name = nameBox.value;
        const age = +ageBox.value;
        if (!id || !name || !age) {
            alert("You must enter Id, Name and Age!")
            return;
        }
        const student = {id, name, age};

        try {
            await axios.put("/students", student);
            await getAll();
        } catch (error) {
            const msg = error.response.data.message;
            alert(msg);
        }

    });

    // add student
    btAdd.addEventListener("click", async function () {
        const name = nameBox.value;
        const age = ageBox.value;
        if (!name || !age) {
            alert("Enter name and age!");
            return;
        }

        const student = {name, age};
        try {
            const response = await axios.post("/students", student);
            await getAll();
        } catch (error) {
            alert("Add student failed - " + error.response.data.message)
        }
    });

    // delete student
    btDelete.addEventListener("click", async function () {
        const id = idBox.value;
        deleteStudent(id);
    })

    async function deleteStudent(id) {
        if (!id) {
            alert("Enter ID!");
            return;
        }
        try {
            await axios.delete(`/students/${id}`);
            await getAll();
        } catch (error) {
            //console.dir(error);
            alert(error.response.data.message);
        }
    }

    window.addEventListener("load", getAll);


    // get all students
    async function getAll() {
        let response = await axios.get("/students");
        const students = response.data;
        let content = "";
        for (const s of students) {
            content += `
                <tr>
                  <td>${s.id}</td>
                  <td>${s.name}</td>
                  <td>${s.age}</td>
                  <td><button class="delete-btn" data-id="${s.id}">X</button></td>
                </tr>
            `;
        }
        tbody.innerHTML = content;
        // to register all delete buttons - get an array of all delete buttons
        const deleteButtons = Array.from(document.getElementsByClassName("delete-btn"));
        deleteButtons.forEach(button => {
            button.addEventListener("click", function () {
                const studentId = button.getAttribute("data-id");
                deleteStudent(studentId);
            });
        });

    }
}